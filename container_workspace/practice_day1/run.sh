#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Day 1 종합실습 - 3-tier 미니 게시판 실행 스크립트
# 교재 [Step 0] ~ [Step 6] 을 그대로 순서대로 실행한다.
#   사용법:  bash run.sh        (board 폴더 안에서 실행)
# ---------------------------------------------------------------------------
set -e

NETWORK="board-net"

echo "=============================================="
echo " [Step 0] 실습 환경 정리하기"
echo "=============================================="
docker ps -a
docker rm -f board-web board-was board-db >/dev/null 2>&1 || true
echo "--- 정리 후 ---"
docker ps -a
echo

echo "=============================================="
echo " [Step 4-1] 전용 네트워크 만들기"
echo "=============================================="
docker network create "${NETWORK}" 2>/dev/null || echo "${NETWORK} 은(는) 이미 있습니다."
docker network ls | grep "${NETWORK}"
echo

echo "=============================================="
echo " [Step 4-2] DB 컨테이너 실행 (PostgreSQL)"
echo "=============================================="
docker run --name board-db \
  --network "${NETWORK}" \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=board \
  -d postgres:17
echo

echo "=============================================="
echo " [Step 5-1] WAS 이미지 빌드 & 실행"
echo "=============================================="
docker build -t board-was:1.0 ./was
docker run --name board-was \
  --network "${NETWORK}" \
  -e DB_HOST=board-db \
  -p 5001:5000 \
  -d board-was:1.0
echo

echo "=============================================="
echo " [Step 5-2] Web 이미지 빌드 & 실행"
echo "=============================================="
docker build -t board-web:1.0 ./web
docker run --name board-web \
  --network "${NETWORK}" \
  -p 8080:80 \
  -d board-web:1.0
echo

echo "WAS 가 DB 에 연결될 때까지 잠시 기다립니다..."
sleep 8

echo "=============================================="
echo " [Step 6] 실행 확인"
echo "=============================================="
docker ps
echo
echo "--- docker logs board-was ---"
docker logs board-was
echo
echo "--- WAS 헬스 체크 (호스트에서 직접) ---"
curl -s http://localhost:5001/api/health || echo "(curl 실패 - 잠시 후 다시 시도해보세요)"
echo
echo
echo "=============================================="
echo " 브라우저에서 http://localhost:8080 접속하세요"
echo "=============================================="
