# ==================================================================
# 1단계 : 빌드 (Builder)
#
# Node 환경에서 npm run build 를 실행해 dist/ 를 만든다.
# 이 단계의 node_modules 는 최종 이미지에 포함되지 않는다.
# ==================================================================
FROM node:22-alpine AS build

WORKDIR /app

# 의존성 파일을 먼저 복사한다.
# 소스만 바뀌었을 때 npm ci 레이어를 캐시에서 재사용하기 위함이다.
COPY package*.json ./
RUN npm ci

COPY . .

# ------------------------------------------------------------------
# Vite 는 VITE_ 접두사 환경변수를 "빌드 시점"에 코드 안으로 치환한다.
# 따라서 API Key 는 컨테이너 실행 시가 아니라 빌드 인자로 전달해야 한다.
# (docker compose 가 .env 의 값을 args 로 넘겨준다)
# ------------------------------------------------------------------
ARG VITE_OPENWEATHER_API_KEY
ENV VITE_OPENWEATHER_API_KEY=$VITE_OPENWEATHER_API_KEY

RUN npm run build


# ==================================================================
# 2단계 : 서빙 (Runtime)
#
# 빌드 결과물인 정적 파일만 nginx 이미지로 옮긴다.
# Node 와 소스코드는 최종 이미지에 남지 않아 용량이 크게 줄어든다.
# ==================================================================
FROM nginx:alpine

# 기본 설정을 우리 SPA 설정으로 교체
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드 단계에서 만들어진 dist 만 가져온다
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
