# Day 1 종합실습 — 3-tier 미니 게시판

**판교캠퍼스 1반 김상욱**

Web(nginx) · WAS(Flask) · DB(PostgreSQL) 세 개의 컨테이너를 `docker run` 과
`docker network` 만으로 연결해 하나의 게시판 서비스를 완성한 실습입니다.
(Docker Compose 는 Day 2 에서 다루므로 사용하지 않았습니다.)

---

## 1. 폴더 구조

```
board/
├── web/                 # Web 티어 (화면)
│   ├── Dockerfile       # 교재 140p 그대로 (FROM / COPY / EXPOSE 3줄)
│   └── index.html       # 글 목록 / 글쓰기 화면
├── was/                 # WAS 티어 (서버)
│   ├── Dockerfile
│   ├── app.py           # Flask API (글 목록/글쓰기/삭제)
│   ├── requirements.txt # flask, psycopg2-binary
│   └── .dockerignore
├── run.sh               # Step 0~6 전체 실행
├── cleanup.sh           # 컨테이너/이미지/네트워크 정리
└── README.md
```

DB 는 공식 이미지(`postgres:17`)를 그대로 쓰므로 별도 폴더가 없습니다.

---

## 2. 요청이 흐르는 길

```
                 ┌─8080─▶ board-web (nginx)      화면(index.html) 전달
브라우저 ────────┤
                 └─5001─▶ board-was (Flask,5000)  글 목록/글쓰기 API
                                │
                                │  DB_HOST=board-db   ← 컨테이너 이름이 곧 주소
                                ▼
                          board-db (PostgreSQL, 5432)
```

- 화면은 nginx 가 주고, 데이터는 WAS 가 줍니다. 화면의 JS 가 `localhost:5001` 로 API 를 호출합니다.
  (교재 Step 5 에서 WAS 를 `-p 5001:5000` 으로 열어두는 이유)
- **DB 는 호스트로 포트를 열지 않습니다.** WAS 만 `board-net` 안에서 `board-db` 라는
  **컨테이너 이름을 그대로 주소처럼** 써서 접속합니다.
- 화면(8080)과 API(5001)는 포트가 달라 브라우저가 '다른 출처'로 보기 때문에,
  `app.py` 에서 CORS 허용 헤더 3줄을 붙여줍니다.

---

## 3. 실행 방법

### 한 번에 실행

```bash
cd board
bash run.sh
```

### 손으로 하나씩 (교재 순서 그대로)

```bash
# [Step 0] 이전 실습 정리
docker ps -a
docker rm -f board-web board-was board-db

# [Step 4] 네트워크 + DB
docker network create board-net
docker run --name board-db --network board-net \
  -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=board \
  -d postgres:17
docker ps

# [Step 5] WAS
docker build -t board-was:1.0 ./was
docker run --name board-was --network board-net \
  -e DB_HOST=board-db -p 5001:5000 -d board-was:1.0

# [Step 5] Web
docker build -t board-web:1.0 ./web
docker run --name board-web --network board-net \
  -p 8080:80 -d board-web:1.0

# [Step 6] 확인
docker ps
docker logs board-was
```

브라우저에서 **http://localhost:8080** 접속 → 글쓰기 → 목록에 나타나면 성공입니다.

### 정리

```bash
bash cleanup.sh
```

---

## 4. 제출 전 캡처할 화면 (실행 증빙)

| 파일명 | 무엇을 캡처하나 |
| --- | --- |
| `01_docker_ps.png` | `docker ps` 결과 — **컨테이너 3개가 모두 Up** 상태 |
| `02_browser.png` | `http://localhost:8080` 화면 — 글을 쓰고 **목록에 뜬 상태** |
| `03_logs.png` | `docker logs board-was` — `[DB 연결 성공] board-db:5432 접속 완료` 줄 |

> 캡처한 이미지는 코드리뷰 PDF 의 "실행 증빙" 페이지에 붙이면 됩니다.

DB 에 실제로 저장됐는지 눈으로 확인하고 싶다면:

```bash
docker exec -it board-db psql -U postgres -d board -c "SELECT * FROM posts;"
```

---

## 5. 자주 나는 에러

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| `port is already allocated` | 8080/5001 을 다른 컨테이너가 이미 씀 | `docker ps -a` 확인 후 `docker rm -f <이름>`, 또는 `-p 8081:80` 으로 변경 |
| `name is already in use` | 같은 이름 컨테이너가 남아있음 | `docker rm -f board-web board-was board-db` |
| 목록이 안 뜨고 "불러오지 못했습니다" | WAS 가 아직 DB 연결 대기 중 | `docker logs board-was` 로 `[DB 연결 성공]` 이 나올 때까지 대기 |
| `could not translate host name "board-db"` | WAS 가 네트워크에 안 붙음 | `--network board-net` 옵션을 빠뜨렸는지 확인 |
| 콘솔에 `CORS policy` 에러 | `app.py` 의 CORS 헤더가 빠졌거나 WAS 가 죽음 | `curl -i http://localhost:5001/api/posts` 로 `Access-Control-Allow-Origin` 확인 |
| `ERR_CONNECTION_REFUSED` (5001) | WAS 를 `-p 5001:5000` 없이 실행했음 | `docker rm -f board-was` 후 `-p` 옵션 넣고 재실행 |
| 글쓰기는 되는데 새로고침하면 사라짐 | DB 컨테이너를 지웠음 | 볼륨 없이 컨테이너를 지우면 데이터도 사라짐 (교재 '기억상실 문제') |
