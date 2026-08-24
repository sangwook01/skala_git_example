"""
WAS (Web Application Server) - 미니 게시판 API

3-tier 구조에서 가운데 층을 담당한다.
  Web(nginx) -> [ WAS(Flask) ] -> DB(PostgreSQL)

DB 접속 정보는 코드에 박아두지 않고 '환경 변수'로 받는다.
(docker run -e DB_HOST=board-db ... 로 전달)
"""

import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """
    화면(Web, 8080)과 이 서버(WAS, 5001)는 포트가 달라서 브라우저가 '다른 출처'로 본다.
    허용해주지 않으면 브라우저가 응답을 막기 때문에 아래 헤더를 붙여준다.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return response


# ---------------------------------------------------------------------------
# 환경 변수로 DB 접속 정보 받기 (기본값은 실습 기준값)
# ---------------------------------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "board-db")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "board")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "mypassword")

APP_PORT = int(os.environ.get("APP_PORT", "5000"))


def get_connection():
    """DB 커넥션을 하나 만들어 돌려준다."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS posts (
    id         SERIAL PRIMARY KEY,
    author     VARCHAR(50)  NOT NULL,
    title      VARCHAR(200) NOT NULL,
    content    TEXT         NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db(retries: int = 30, delay: int = 2) -> None:
    """
    DB 가 준비될 때까지 기다렸다가 테이블을 만든다.

    DB 컨테이너는 '실행됨(Up)' 상태가 되어도 내부 초기화에 몇 초가 더 걸린다.
    그래서 한 번 실패했다고 바로 죽지 않고 재시도한다.
    """
    for attempt in range(1, retries + 1):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
            conn.commit()
            print(f"[DB 연결 성공] {DB_HOST}:{DB_PORT} 접속 완료", flush=True)
            return
        except psycopg2.OperationalError as exc:
            print(
                f"[DB 연결 대기] {attempt}/{retries} - {DB_HOST}:{DB_PORT} ({exc.__class__.__name__})",
                flush=True,
            )
            time.sleep(delay)
        finally:
            if conn is not None:
                conn.close()

    raise RuntimeError(f"[DB 연결 실패] {DB_HOST}:{DB_PORT} 에 접속할 수 없습니다.")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    """WAS 와 DB 가 살아있는지 확인하는 용도."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return jsonify(status="ok", db_host=DB_HOST, db_name=DB_NAME)
    except psycopg2.Error as exc:
        return jsonify(status="error", message=str(exc)), 503
    finally:
        if conn is not None:
            conn.close()


@app.get("/api/posts")
def list_posts():
    """글 목록 조회 (최신순)."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, author, title, content, created_at "
                "FROM posts ORDER BY id DESC;"
            )
            rows = cur.fetchall()

        posts = [
            {
                "id": row["id"],
                "author": row["author"],
                "title": row["title"],
                "content": row["content"],
                "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            }
            for row in rows
        ]
        return jsonify(count=len(posts), posts=posts)
    except psycopg2.Error as exc:
        return jsonify(status="error", message=str(exc)), 503
    finally:
        if conn is not None:
            conn.close()


@app.post("/api/posts")
def create_post():
    """글 쓰기 - 화면에서 받은 내용을 DB 에 저장한다."""
    data = request.get_json(silent=True) or {}

    author = (data.get("author") or "").strip()
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not author or not title or not content:
        return jsonify(status="error", message="작성자, 제목, 내용은 모두 필요합니다."), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (author, title, content) "
                "VALUES (%s, %s, %s) RETURNING id, created_at;",
                (author, title, content),
            )
            new_id, created_at = cur.fetchone()
        conn.commit()

        print(f"[글 저장] id={new_id} author={author} title={title}", flush=True)
        return (
            jsonify(
                status="ok",
                id=new_id,
                created_at=created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ),
            201,
        )
    except psycopg2.Error as exc:
        if conn is not None:
            conn.rollback()
        return jsonify(status="error", message=str(exc)), 503
    finally:
        if conn is not None:
            conn.close()


@app.delete("/api/posts/<int:post_id>")
def delete_post(post_id: int):
    """글 삭제."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE id = %s;", (post_id,))
            deleted = cur.rowcount
        conn.commit()

        if deleted == 0:
            return jsonify(status="error", message="해당 글이 없습니다."), 404
        return jsonify(status="ok", id=post_id)
    except psycopg2.Error as exc:
        if conn is not None:
            conn.rollback()
        return jsonify(status="error", message=str(exc)), 503
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=APP_PORT)
