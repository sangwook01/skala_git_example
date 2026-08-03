# SKALA-SHOP API

온라인 쇼핑몰 백엔드 REST API 실습 과제 구현체입니다.
Controller → Service → Repository 계층형 구조(Layered Architecture)로 작성되었습니다.

## 기술 스택
- Spring Boot 3.3.0 / Java 17
- Spring Data JPA + H2 (in-memory)
- Spring AOP (API 로깅)
- JWT (jjwt 0.11.5) 인증 - Cookie(`bff-access`) 전달
- Gradle

## 실행 방법

```bash
# 로컬 실행
./gradlew bootRun

# 빌드 후 jar 실행
./gradlew clean build -x test
java -jar build/libs/skala-shop-api-0.0.1-SNAPSHOT.jar

# Docker 실행
docker build -t shop-api:1.0 .
docker run -d -p 8080:8080 shop-api:1.0
```

H2 콘솔: http://localhost:8080/h2-console (JDBC URL: `jdbc:h2:mem:shopdb`, 계정 `sa` / 빈 비밀번호)

## 패키지 구조

```
com.sk.skala.shopapi
├─ ShopApiApplication.java        # @SpringBootApplication (메인)
├─ aop/                           # API 요청/응답 로깅 (AOP)
├─ common/                        # Response, PagedList, SessionHandler(JWT)
├─ controller/                    # ProductController, CustomerController
├─ data/table/                    # Product, Customer, OrderItem (JPA 엔티티)
├─ data/dto/                      # OrderItemDto, OrderListDto, OrderRequest, CustomerSession
├─ exception/                     # Error, ResponseException, ParameterException, GlobalExceptionHandler
├─ repository/                    # ProductRepository, CustomerRepository, OrderItemRepository
├─ service/                       # ProductService, CustomerService
└─ tools/                         # StringUtil, JwtUtil
```

## API 목록

| Resource | Method | URI | 설명 |
|---|---|---|---|
| 상품 | GET | /api/products, /api/products/list | 상품 전체 목록 조회 (페이징: offset, count) |
| 상품 | GET | /api/products/{id} | 개별 상품 상세 조회 |
| 상품 | POST | /api/products | 상품 등록 |
| 상품 | PUT | /api/products | 상품 정보 수정 |
| 상품 | DELETE | /api/products | 상품 삭제 |
| 고객 | GET | /api/customers, /api/customers/list | 고객 전체 목록 조회 (페이징: offset, count) |
| 고객 | GET | /api/customers/{customerId} | 고객 상세 + 주문 상품 목록 조회 |
| 고객 | GET | /api/customers/{customerId}/products | 고객이 보유(주문)한 상품 정보만 조회 |
| 고객 | POST | /api/customers | 회원가입 (초기 포인트 100만 지급, 고정값) |
| 고객 | POST | /api/customers/login | 로그인 → JWT 발급 (Set-Cookie: bff-access) |
| 고객 | PUT | /api/customers | 고객 정보(포인트 등) 수정 |
| 고객 | DELETE | /api/customers/{customerId}, /api/customers (body) | 고객 삭제 |
| 주문 | POST | /api/customers/order | 상품 주문 (JWT 필요, 포인트 차감) |
| 주문 | POST | /api/customers/cancel | 주문 취소 (JWT 필요, 포인트 환급) |

> `GET /api/customers/{customerName}` (이름으로 조회) 항목은 실습 명세의 API 목록 표에는
> 있지만, `Customer` 엔티티에는 애초에 `customerName` 필드가 정의되어 있지 않고 경로도
> `{customerId}`와 완전히 동일한 패턴이라 함께 매핑할 수 없습니다. 명세 자체의 오류로 보고
> 구현하지 않았습니다.

## API 호출 흐름 예시 (End-to-End)

```
# 1) 회원가입 (초기 포인트 자동 지급 - 요청 본문의 포인트 값은 무시됨)
POST /api/customers
{ "customerId": "skala01", "customerPassword": "pw1234" }

# 2) 로그인 -> JWT 발급 (이후 요청에 Cookie 자동 첨부)
POST /api/customers/login
{ "customerId": "skala01", "customerPassword": "pw1234" }
-> Set-Cookie: bff-access=<JWT>

# 3) 상품 목록 조회
GET /api/products

# 4) 상품 주문 - 무선마우스(id=1) 2개 (JWT 필요, 포인트 차감)
POST /api/customers/order
{ "productId": 1, "quantity": 2 }

# 5) 내 주문 확인
GET /api/customers/skala01

# 6) 주문 취소 - 1개 취소 (포인트 환급)
POST /api/customers/cancel
{ "productId": 1, "quantity": 1 }
```

## 비즈니스 규칙 & 예외 처리

| 구분 | 규칙 |
|---|---|
| 포인트 | 보유 포인트로 주문, 부족 시 주문 거부 (`INSUFFICIENT_FUNDS`) |
| 주문 수량 | 재주문 시 수량 누적, 취소 시 수량 차감 (0이면 삭제). productId/quantity 누락 또는 quantity가 0 이하면 `ParameterException` |
| 인증(JWT) | 주문/취소는 로그인 필수 - Cookie(`bff-access`)의 JWT를 검증해 고객 식별 |
| 입력 검증 | 상품명/가격 등 필수값 검증 실패 시 `ParameterException` |
| 예외 처리 | 없는 상품/고객 조회 시 `DATA_NOT_FOUND` (전역 예외 처리) |
| 트랜잭션 | 주문/취소는 `@Transactional`로 원자적 처리 (포인트·수량 일관성) |

## JPA / @Query 처리 포인트

- `ProductRepository.findByProductName` : Query Method (상품명 중복 체크)
- `OrderItemRepository.findByCustomer_CustomerId` : 속성 순회(Property Traversal)로
  `OrderItem.customer.customerId` 값을 기준 조회
- `OrderItemRepository.findByCustomerAndProduct` : 특정 고객이 특정 상품을 이미
  보유(주문)하고 있는지 확인 (주문 시 수량 누적 / 취소 시 수량 차감 판단에 사용)
- `OrderItemRepository.findItemsWithProductByCustomerId` : `@Query` + JPQL `fetch join`으로
  고객의 주문 상품 목록 조회 시 N+1 문제를 방지하고 정렬까지 함께 처리

## JWT 적용 여부에 따른 차이

이 프로젝트는 로그인 식별을 `SessionHandler` 한 곳에서만 담당하도록 분리해 두어서,
JWT를 쓰든 안 쓰든 Controller/Service 계층의 코드는 그대로입니다. 차이는 아래와 같습니다.

| 구분 | JWT 미적용 (단순 쿠키) | JWT 적용 (현재 구현) |
|---|---|---|
| 로그인 성공 시 쿠키 값 | `customerId`를 그대로 저장 | `JwtUtil`로 서명한 토큰(`customerId`를 subject로 포함) 저장 |
| 주문/취소 시 식별 | 쿠키 값을 그대로 `customerId`로 사용 | 쿠키의 토큰을 서명 검증 후 subject를 추출 |
| 위조 방어 | 없음 - 쿠키 값을 바꾸면 다른 사람 행세 가능 | 비밀키 없이는 위조 불가능 (서명 불일치 시 거부) |
| 만료 처리 | 없음 (쿠키 자체 만료 시간만 존재) | 토큰의 `exp` 클레임으로 서버가 명시적으로 만료 판단 |
| 필요한 것 | 없음 | `jjwt` 의존성, `JwtUtil`, `application.yml`의 `jwt.secret`/`jwt.expiration-millis` |
| 예외 처리 | `Error.UNAUTHORIZED`(로그인 필요) 하나만 사용 | 쿠키 없음(`UNAUTHORIZED`)과 토큰 무효/만료(`NOT_AUTHENTICATED`)를 구분 |

> 참고: 실습 초반에는 JWT 없이 쿠키에 `customerId`만 담아 빠르게 흐름을 검증한 뒤,
> 이후 `SessionHandler`만 JWT 버전으로 바꿔 끼우는 방식으로 단계적으로 진행할 수도 있습니다.
> (`storeAccessToken` / `getCurrentCustomerId` 두 메서드의 시그니처만 유지하면 됨)

## 원본 구현에서 발견 및 수정한 문제

1. **상품 등록 시 `id`를 `0L`로 강제 세팅하던 버그** — 실습 슬라이드는 "신규 상품의 ID는
   0L로 세팅"이라고 안내하지만, `@GeneratedValue(strategy = IDENTITY)`에서는 id가 `null`일
   때만 신규(INSERT) 엔티티로 인식됩니다. `0L`처럼 값을 채워 넣으면 Hibernate가 이를 기존
   엔티티로 오인해 갱신을 시도하다 실패합니다. → `id`를 `null`로 유지하도록 수정.
2. **고객 목록 조회 시 비밀번호 평문 노출** — `GET /api/customers`(목록) 응답에 비밀번호
   필드가 그대로 포함되어 있었음 → 응답 전 `null` 처리.
3. **회원가입 시 클라이언트가 초기 포인트를 임의로 지정 가능** — 요청 본문에 `customerPoint`를
   실어 보내면 그 값이 그대로 저장되는 문제 → 항상 서버 고정값(100만)으로만 지급하도록 수정.
4. **주문/취소 수량 검증 누락** — `quantity`가 없거나 0 이하(음수 포함)여도 그대로 처리되어,
   예를 들어 음수 수량으로 주문 시 포인트 부족 검사를 우회하고 오히려 포인트가 증가하는
   취약점이 있었음 → `productId`/`quantity` 누락 및 0 이하 값 검증 추가.
5. **API 경로 표기 불일치** — 실습 명세의 "API 목록" 요약표와 상세 구현 예시 코드가 상품/고객
   목록 조회 경로를 각각 다르게 제시(`/api/products` vs `/api/products/list` 등) → 두 경로
   모두 지원하도록 처리. 고객 삭제도 마찬가지로 경로변수 방식과 `@RequestBody` 방식을 모두 지원.
6. **`{customerId}` / `{customerName}` 경로 중복 명세** — 위 안내 참고 (엔티티에 필드 자체가
   없고 경로도 동일해 구현 불가능한 명세 오류).
7. **JWT 인증 실패 사유 구분** — 쿠키가 아예 없는 경우(로그인 필요)와, 쿠키는 있지만 서명이
   무효하거나 만료된 경우(재로그인 필요)를 각각 `UNAUTHORIZED` / `NOT_AUTHENTICATED`로 구분.
