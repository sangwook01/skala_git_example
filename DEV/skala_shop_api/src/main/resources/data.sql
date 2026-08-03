INSERT INTO product (product_name, product_price) VALUES ('무선마우스', 15000);
INSERT INTO product (product_name, product_price) VALUES ('블루투스키보드', 29000);
INSERT INTO product (product_name, product_price) VALUES ('USB허브', 39000);


-- ============================================
-- [A] 페이징(offset/count) 테스트용 추가 상품
--     기존 3개 + 아래 10개 = 총 13개 -> count=5 기준 페이지 3개로 나뉨
-- ============================================
INSERT INTO product (product_name, product_price) VALUES ('기계식키보드', 89000);
INSERT INTO product (product_name, product_price) VALUES ('27인치모니터', 259000);
INSERT INTO product (product_name, product_price) VALUES ('웹캠', 45000);
INSERT INTO product (product_name, product_price) VALUES ('노트북거치대', 32000);
INSERT INTO product (product_name, product_price) VALUES ('데스크매트', 19000);
INSERT INTO product (product_name, product_price) VALUES ('블루투스스피커', 68000);
INSERT INTO product (product_name, product_price) VALUES ('usb-c허브', 42000);
INSERT INTO product (product_name, product_price) VALUES ('헤드셋', 79000);
INSERT INTO product (product_name, product_price) VALUES ('마우스패드', 12000);
INSERT INTO product (product_name, product_price) VALUES ('모니터암', 55000);

-- ============================================
-- [B] 경계값(포인트/가격) 테스트 전용 상품
-- ============================================
-- 초고가 상품: 기본 초기 포인트(100만)로는 1개도 못 사는 가격
--             -> 아무 신규 회원이나 이 상품을 quantity=1로 주문하면 바로 INSUFFICIENT_FUNDS 재현
INSERT INTO product (product_name, product_price) VALUES ('프리미엄모니터(테스트용)', 2000000);

-- 초저가 상품: 대량 수량 주문 테스트용 (quantity=9999 -> 999900원, 100만 포인트로 간신히 성공)
INSERT INTO product (product_name, product_price) VALUES ('볼펜(테스트용)', 100);

-- ============================================
-- [C] 고객 시드 데이터 - 다양한 포인트 시나리오
--     (회원가입 API를 거치지 않고 바로 로그인해서 테스트 가능)
--     비밀번호는 모두 'pw1234' 로 통일
-- ============================================
-- 정상 포인트 고객 (API로 가입했을 때와 동일한 100만 포인트)
INSERT INTO customer (customer_id, customer_password, customer_point) VALUES ('normal01', 'pw1234', 1000000);

-- 포인트 부족 테스트 전용 고객 (무선마우스 1개도 못 삼 - 15000 > 3000)
INSERT INTO customer (customer_id, customer_password, customer_point) VALUES ('poor01', 'pw1234', 3000);

-- 0포인트 고객 (극단값 - 어떤 주문도 실패해야 정상)
INSERT INTO customer (customer_id, customer_password, customer_point) VALUES ('zero01', 'pw1234', 0);

-- 부자 고객 (프리미엄모니터 같은 고가 상품도 주문 가능해야 함)
INSERT INTO customer (customer_id, customer_password, customer_point) VALUES ('rich01', 'pw1234', 5000000);

-- 경계값 정확 일치 고객: 무선마우스(15000) 딱 1개 살 수 있는 포인트
-- -> 주문 성공 후 잔여 포인트는 정확히 0이어야 함 (< 조건이라 0은 실패하면 안 됨)
INSERT INTO customer (customer_id, customer_password, customer_point) VALUES ('edge01', 'pw1234', 15000);

-- ============================================
-- [D] 기존 주문내역(OrderItem) 시드 데이터
--     -> 주문 API를 먼저 호출하지 않고도 취소(cancel) API를 바로 테스트하기 위함
--     상품 id를 하드코딩하지 않고 상품명으로 서브쿼리 조회 (삽입 순서가 바뀌어도 안전)
-- ============================================
-- rich01 고객이 무선마우스 5개를 이미 보유한 상태로 시작
-- -> POST /api/customers/cancel { "productId": 1, "quantity": 2 } : 부분 취소(3개 남음)
-- -> POST /api/customers/cancel { "productId": 1, "quantity": 5 } : 전량 취소(항목 삭제)
-- -> POST /api/customers/cancel { "productId": 1, "quantity": 6 } : 초과 취소(400 INSUFFICIENT_QUANTITY)
INSERT INTO order_item (customer_id, product_id, quantity)
VALUES ('rich01', (SELECT id FROM product WHERE product_name = '무선마우스'), 5);

-- rich01 고객이 기존에 보유한 무선마우스 5개(75000원)만큼 포인트가 이미 차감된 상태로 맞춰줌
-- (5000000 - 75000 = 4925000) - 위 [C]에서 넣은 값을 덮어씀
UPDATE customer SET customer_point = 4925000 WHERE customer_id = 'rich01';