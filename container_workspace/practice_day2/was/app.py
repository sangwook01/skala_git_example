"""
WAS (Web Application Server) - 미니 게시판  [Day 2 / 방법 3: 서버가 HTML 을 생성]

Day 1 (방법 1) 과의 차이
  Day 1 : Flask 가 JSON 만 응답하고, 화면은 web 의 index.html 이 JS 로 그렸다.
  Day 2 : Flask 가 render_template 으로 완성된 HTML 을 응답한다.
          web 컨테이너의 index.html 은 환영 페이지 역할만 한다.

이 방식으로 바뀌면서 얻은 것
  - CORS 헤더가 필요 없어졌다. 브라우저가 WAS 와 같은 출처에서 화면을 받기 때문.
  - 화면이 WAS 포트를 알 필요가 없어졌다. 폼이 자기 자신에게 제출하면 되므로.

추가 기능 : 검색 / 수정 / 삭제
"""

import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

app = Flask(__name__)

# flash 메시지(저장 완료, 삭제 완료 ...)를 쓰려면 세션 서명용 키가 필요하다.
# 값은 .env 에서 주입한다.
app.secret_key = os.environ.get("SECRET_KEY", "day2-practice-secret")

# ---------------------------------------------------------------------------
# 환경 변수로 DB 접속 정보 받기
# ---------------------------------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "board")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

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

# Day 1 에 만든 테이블에는 updated_at 이 없다.
# 볼륨에 남아있는 기존 데이터를 살리면서 컬럼만 추가한다.
ALTER_TABLE_SQL = """
ALTER TABLE posts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
"""


def init_db(retries: int = 30, delay: int = 2) -> None:
    """
    DB 가 준비될 때까지 기다렸다가 테이블을 만든다.

    DB 컨테이너는 '실행됨(Up)' 상태가 되어도 내부 초기화에 몇 초가 더 걸린다.
    compose 의 depends_on 은 순서만 보장하고 준비 완료는 보장하지 않으므로,
    여기서 재시도로 기다린다.
    """
    for attempt in range(1, retries + 1):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
                cur.execute(ALTER_TABLE_SQL)
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


def fetch_posts(keyword: str = ""):
    """글 목록을 가져온다. keyword 가 있으면 제목·내용·작성자에서 검색한다."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if keyword:
                # %s 로 값을 넘겨 SQL Injection 을 막는다 (문자열 이어붙이기 금지)
                cur.execute(
                    "SELECT * FROM posts "
                    "WHERE title ILIKE %s OR content ILIKE %s OR author ILIKE %s "
                    "ORDER BY id DESC;",
                    (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
                )
            else:
                cur.execute("SELECT * FROM posts ORDER BY id DESC;")
            return cur.fetchall()
    finally:
        conn.close()


def fetch_post(post_id: int):
    """글 하나를 가져온다. 없으면 None."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM posts WHERE id = %s;", (post_id,))
            return cur.fetchone()
    finally:
        conn.close()


def validate(author: str, title: str, content: str):
    """입력값 검사. 문제가 있으면 메시지를, 없으면 None 을 돌려준다."""
    if not author or not title or not content:
        return "작성자, 제목, 내용은 모두 입력해야 합니다."
    if len(author) > 50:
        return "작성자는 50자를 넘을 수 없습니다."
    if len(title) > 200:
        return "제목은 200자를 넘을 수 없습니다."
    return None


# ---------------------------------------------------------------------------
# 화면 (서버가 HTML 을 만들어 응답한다)
# ---------------------------------------------------------------------------
@app.get("/")
def list_page():
    """글 목록 + 검색."""
    keyword = (request.args.get("q") or "").strip()
    posts = fetch_posts(keyword)
    return render_template("list.html", posts=posts, keyword=keyword)


@app.get("/posts/new")
def new_page():
    """글쓰기 폼."""
    return render_template("form.html", post=None, mode="new")


@app.post("/posts/new")
def create_post():
    """글쓰기 처리."""
    author = (request.form.get("author") or "").strip()
    title = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()

    error = validate(author, title, content)
    if error:
        flash(error, "error")
        # 입력하던 내용을 잃지 않도록 폼에 돌려준다
        return render_template(
            "form.html",
            post={"author": author, "title": title, "content": content},
            mode="new",
        ), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (author, title, content) "
                "VALUES (%s, %s, %s) RETURNING id;",
                (author, title, content),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
    finally:
        conn.close()

    print(f"[글 저장] id={new_id} author={author} title={title}", flush=True)
    flash("글이 저장되었습니다.", "ok")
    return redirect(url_for("detail_page", post_id=new_id))


@app.get("/posts/<int:post_id>")
def detail_page(post_id: int):
    """글 상세."""
    post = fetch_post(post_id)
    if post is None:
        flash("해당 글을 찾을 수 없습니다.", "error")
        return redirect(url_for("list_page"))
    return render_template("detail.html", post=post)


@app.get("/posts/<int:post_id>/edit")
def edit_page(post_id: int):
    """글 수정 폼."""
    post = fetch_post(post_id)
    if post is None:
        flash("해당 글을 찾을 수 없습니다.", "error")
        return redirect(url_for("list_page"))
    return render_template("form.html", post=post, mode="edit")


@app.post("/posts/<int:post_id>/edit")
def update_post(post_id: int):
    """글 수정 처리."""
    author = (request.form.get("author") or "").strip()
    title = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()

    error = validate(author, title, content)
    if error:
        flash(error, "error")
        return render_template(
            "form.html",
            post={"id": post_id, "author": author, "title": title, "content": content},
            mode="edit",
        ), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE posts "
                "SET author = %s, title = %s, content = %s, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = %s;",
                (author, title, content, post_id),
            )
            updated = cur.rowcount
        conn.commit()
    finally:
        conn.close()

    if updated == 0:
        flash("해당 글을 찾을 수 없습니다.", "error")
        return redirect(url_for("list_page"))

    print(f"[글 수정] id={post_id} title={title}", flush=True)
    flash("글이 수정되었습니다.", "ok")
    return redirect(url_for("detail_page", post_id=post_id))


@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id: int):
    """
    글 삭제 처리.

    HTML 폼은 GET 과 POST 만 보낼 수 있어서 DELETE 대신 POST 를 쓴다.
    또한 삭제를 GET 으로 만들면 주소만 눌러도 지워지므로 POST 여야 한다.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE id = %s;", (post_id,))
            deleted = cur.rowcount
        conn.commit()
    finally:
        conn.close()

    if deleted == 0:
        flash("해당 글을 찾을 수 없습니다.", "error")
    else:
        print(f"[글 삭제] id={post_id}", flush=True)
        flash("글이 삭제되었습니다.", "ok")
    return redirect(url_for("list_page"))


@app.get("/health")
def health():
    """컨테이너가 살아있는지 확인하는 용도."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return {"status": "ok", "db_host": DB_HOST, "db_name": DB_NAME}
    except psycopg2.Error as exc:
        return {"status": "error", "message": str(exc)}, 503
    finally:
        if conn is not None:
            conn.close()


# ---------------------------------------------------------------------------
# init_db() 를 __main__ 블록 밖에 둔다.
# 이렇게 하면 gunicorn 이나 flask CLI 처럼 모듈을 import 하는 방식으로 실행해도
# 테이블 생성이 건너뛰어지지 않는다. (Day 1 코드 리뷰에서 나온 개선 사항)
# CREATE TABLE IF NOT EXISTS 이므로 여러 번 실행돼도 안전하다.
# ---------------------------------------------------------------------------
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)
