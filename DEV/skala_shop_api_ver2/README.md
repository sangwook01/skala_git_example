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

아래 표는 실습 명세의 "API 목록" 표(스크린샷 기준)와 **URI가 정확히 동일**합니다.

| Resource | Method | URI | 설명 |
|---|---|---|---|
| 상품 | GET | /api/products | 상품 전체 목록 조회 (페이징: offset, count) |
| 상품 | GET | /api/products/{id} | 개별 상품 상세 조회 |
| 상품 | POST | /api/products | 상품 등록 |
| 상품 | PUT | /api/products | 상품 정보 수정 |
| 상품 | DELETE | /api/products | 상품 삭제 |
| 고객 | GET | /api/customers | 고객 전체 목록 조회 (페이징: offset, count) |
| 고객 | GET | /api/customers/{customerId} | ID에 해당하는 고객 상세 정보 |
| 고객 | GET | /api/customers/{customerName} | Name에 해당하는 고객 상세 정보 |
| 고객 | POST | /api/customers | 회원가입 (초기 포인트 100만 지급, 고정값) |
| 고객 | POST | /api/customers/login | 로그인 → JWT 발급 (Set-Cookie: bff-access) |
| 고객 | PUT | /api/customers | 고객 정보 변경 |
| 고객 | DELETE | /api/customers/{customerId} | 고객 정보 삭제 |
| 고객 | GET | /api/customers/{customerId}/products | 고객의 상품 정보 조회 |
| 주문 | POST | /api/customers/order | 고객의 상품 주문 (JWT 필요, 포인트 차감) |
| 주문 | POST | /api/customers/cancel | 고객의 주문 취소 (JWT 필요, 포인트 환급) |

> **`GET /api/customers/{customerId}` 와 `GET /api/customers/{customerName}`은 URI 패턴이
> 완전히 동일**(경로변수 이름만 다름)해서 Spring에서 별도 라우팅으로 나눌 수 없습니다.
> 그래서 하나의 엔드포인트(`CustomerController.getCustomerByIdOrName`)가 전달받은 값으로
> **먼저 customerId로 조회하고, 없으면 customerName으로 재조회**하는 방식으로 두 표 행을
> 모두 지원합니다. 이를 위해 `Customer` 엔터티에 원래 실습 1-2 명세에는 없던
> `customerName`(선택, unique) 필드를 추가했습니다 — 회원가입/수정 시 값을 넣지 않으면
> 그대로 null로 남고 ID로만 조회됩니다.

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

## [추가 기능] 특별할인 / 선착순 이벤트

기존 상품·고객·주문 로직(`ProductService`, `CustomerService`, `OrderItem` 등)은 전혀 수정하지 않고,
완전히 별도의 엔티티/리포지토리/서비스/컨트롤러로 아래 두 기능을 추가했습니다.
`GET/POST /api/products`, `/api/customers/order`, `/api/customers/cancel` 등 기존 API는
이전과 100% 동일하게 동작합니다.

### 추가된 파일
```
data/table/   ProductDiscount, FlashSaleEvent, EventParticipation
data/dto/     DiscountRequest, EventRequest, EventJoinRequest
repository/   ProductDiscountRepository, FlashSaleEventRepository, EventParticipationRepository
service/      PromotionService
controller/   PromotionController (/api/promotions/**)
```
`spring.jpa.hibernate.ddl-auto: update` 설정 덕분에 새 테이블(`product_discount`,
`flash_sale_event`, `event_participation`)은 앱 기동 시 자동으로 생성됩니다.
(테스트 데이터는 요청하신 대로 `data.sql`에는 추가하지 않았습니다 - 직접 관리하시면 됩니다.)

### API 목록

| 기능 | Method | URI | 설명 |
|---|---|---|---|
| 특별할인 | POST | /api/promotions/discounts | 상품에 기간 한정 할인율 등록 (관리자용) |
| 특별할인 | GET | /api/promotions/discounts/{productId} | 현재 할인 적용 여부·할인가 조회 |
| 특별할인 | POST | /api/promotions/discounts/order | 할인가로 상품 주문 (로그인 필요) |
| 선착순 이벤트 | POST | /api/promotions/events | 이벤트 등록: 상품·이벤트가·수량·기간 (관리자용) |
| 선착순 이벤트 | GET | /api/promotions/events/{eventId} | 이벤트 상세(잔여 수량 포함) 조회 |
| 선착순 이벤트 | POST | /api/promotions/events/{eventId}/join | 이벤트 참여(=이벤트가로 주문, 로그인 필요) |

### 호출 예시

```
# 1) 무선마우스(id=1)에 20% 할인 등록 (지금부터 1시간)
POST /api/promotions/discounts
{ "productId": 1, "discountRate": 0.2, "startAt": "2026-07-31T00:00:00", "endAt": "2026-07-31T23:59:59" }

# 2) 할인 적용 여부 확인
GET /api/promotions/discounts/1
-> { "originalPrice": 15000, "discountedPrice": 12000.0, "discountActive": true, "discountRate": 0.2 }

# 3) 로그인 후 할인가로 주문 (일반 /api/customers/order 아님, 전용 API)
POST /api/promotions/discounts/order
{ "productId": 1, "quantity": 2 }
-> 12000 * 2 = 24000 포인트 차감

# 4) 블루투스키보드(id=2)로 선착순 이벤트 등록 - 특가 15000원, 선착순 3명
POST /api/promotions/events
{ "productId": 2, "eventPrice": 15000, "totalQuantity": 3,
  "startAt": "2026-07-31T00:00:00", "endAt": "2026-07-31T23:59:59" }
-> 응답의 id를 eventId로 사용 (예: 1)

# 5) 로그인 후 이벤트 참여
POST /api/promotions/events/1/join
{ "quantity": 1 }
-> 성공 시 이벤트단가로 포인트 차감 / 잔여 수량 3->2
-> 이미 참여한 고객이 다시 요청하면 409 EVENT_ALREADY_PARTICIPATED
-> 잔여 수량 소진 후 요청하면 409 EVENT_SOLD_OUT
```

### 새 예외 코드

| 코드 | 상태 | 상황 |
|---|---|---|
| `DISCOUNT_NOT_AVAILABLE` | 400 | 해당 상품에 지금 유효한 할인이 없음 |
| `EVENT_NOT_AVAILABLE` | 400 | 이벤트 기간이 아니거나 비활성화됨 |
| `EVENT_SOLD_OUT` | 409 | 선착순 수량 소진 |
| `EVENT_ALREADY_PARTICIPATED` | 409 | 이미 참여한 고객의 재참여 시도 |

### 선착순 동시성 처리

여러 명이 동시에 `POST /api/promotions/events/{id}/join`을 호출해도 정해진 수량 이상
판매되지 않도록, 잔여 수량 차감을 "읽고 판단 후 저장"이 아니라 **조건부 UPDATE 한 문장**으로 처리합니다.

```java
@Modifying(clearAutomatically = true)
@Query("update FlashSaleEvent f set f.remainingQuantity = f.remainingQuantity - :qty " +
       "where f.id = :id and f.remainingQuantity >= :qty")
int decrementIfAvailable(@Param("id") Long id, @Param("qty") int qty);
```

이 UPDATE의 영향받은 row 수가 0이면 품절로 판단합니다. `joinFlashSaleEvent()` 전체가
`@Transactional`이므로, 차감 이후 단계(포인트 부족, 중복 참여 등)에서 예외가 나면 해당 차감을
포함한 모든 변경이 자동으로 롤백되어 별도의 수동 복구 코드가 필요 없습니다.

### 알려진 설계상 트레이드오프

기존 `OrderItem`에는 "구매 당시 단가"를 저장하는 필드가 없습니다. 따라서 할인/이벤트로
구매한 수량도 이후 `/api/customers/cancel`로 취소하면 취소 시점의 **정상 상품가**로
환급됩니다(할인가/이벤트가로 환급되지 않음). 이는 새로 생긴 문제가 아니라 기존 시스템이
애초에 가격 스냅샷을 남기지 않는 구조이기 때문이며, "기존 로직 유지"라는 요청에 따라
`OrderItem` 스키마는 변경하지 않았습니다. 구매 시점 단가를 정확히 보존하려면
`OrderItem`에 단가 필드를 추가하는 스키마 변경이 필요합니다(원하시면 별도로 반영해드릴 수 있습니다).

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
5. **API 경로 표기 불일치 (해결됨)** — 실습 명세의 "API 목록" 요약표와 상세 구현 예시 코드가
   상품/고객 목록 조회 경로를 각각 다르게 제시(`/api/products` vs `/api/products/list` 등)한
   적이 있어 한때 두 경로를 모두 열어뒀으나, 이후 **API 목록 표와 정확히 동일하게** 맞추기로
   하여 `/list` 별칭과 고객 삭제의 `@RequestBody` 버전은 제거하고 표에 있는 경로만 남김.
6. **`{customerId}` / `{customerName}` 경로 지원 (구현 완료)** — 두 표 행이 URI 패턴이
   완전히 동일해 별도 라우팅이 불가능하므로, 하나의 엔드포인트가 customerId로 먼저 조회하고
   없으면 customerName으로 재조회하도록 구현. 이를 위해 `Customer`에 원래 실습 1-2 명세에는
   없던 `customerName`(선택, unique) 필드를 추가함.
7. **JWT 인증 실패 사유 구분** — 쿠키가 아예 없는 경우(로그인 필요)와, 쿠키는 있지만 서명이
   무효하거나 만료된 경우(재로그인 필요)를 각각 `UNAUTHORIZED` / `NOT_AUTHENTICATED`로 구분.
