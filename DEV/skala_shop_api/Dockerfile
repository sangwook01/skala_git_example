# 1) 빌드 스테이지 (Gradle 빌드)
FROM gradle:8.9-jdk17 AS build
WORKDIR /app
COPY . .
RUN gradle clean build -x test

# 2) 실행 스테이지 (경량 JRE 이미지)
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

# 빌드: docker build -t shop-api:1.0 .
# 실행: docker run -d -p 8080:8080 shop-api:1.0
