package com.sk.skala.shopapi.service;

import com.sk.skala.shopapi.common.Response;
import com.sk.skala.shopapi.common.SessionHandler;
import com.sk.skala.shopapi.data.table.Customer;
import com.sk.skala.shopapi.data.table.EventParticipation;
import com.sk.skala.shopapi.data.table.FlashSaleEvent;
import com.sk.skala.shopapi.data.table.OrderItem;
import com.sk.skala.shopapi.data.table.Product;
import com.sk.skala.shopapi.data.table.ProductDiscount;
import com.sk.skala.shopapi.data.dto.OrderRequest;
import com.sk.skala.shopapi.exception.Error;
import com.sk.skala.shopapi.exception.ParameterException;
import com.sk.skala.shopapi.exception.ResponseException;
import com.sk.skala.shopapi.repository.CustomerRepository;
import com.sk.skala.shopapi.repository.EventParticipationRepository;
import com.sk.skala.shopapi.repository.FlashSaleEventRepository;
import com.sk.skala.shopapi.repository.OrderItemRepository;
import com.sk.skala.shopapi.repository.ProductDiscountRepository;
import com.sk.skala.shopapi.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

/**
 * [추가 기능] 특별할인(Discount) / 선착순 이벤트(FlashSaleEvent) 전용 서비스
 *
 * 설계 원칙: 기존 ProductService/CustomerService의 코드는 단 한 줄도 수정하지 않는다.
 * - 기존 "/api/products", "/api/customers/order", "/api/customers/cancel"은 이전과 완전히 동일하게 동작한다.
 * - 할인/이벤트 주문은 이 클래스의 전용 메서드(placeDiscountOrder, joinFlashSaleEvent)를 통해서만 이루어지며,
 *   Customer/Product/OrderItem 테이블은 기존과 동일하게 재사용한다(같은 상품을 "주문"한다는 도메인 의미는 동일하므로).
 *
 * 주의(설계상 트레이드오프): 기존 OrderItem에는 "구매 당시 단가"를 저장하는 필드가 없다.
 * 따라서 할인/이벤트로 구매한 수량도 기존과 동일하게 나중에 /api/customers/cancel로 취소하면
 * "취소 시점의 정상 상품가"로 환급된다(할인가로 환급되지 않음). 이는 기존 시스템이 애초에
 * 가격 스냅샷을 남기지 않는 구조이기 때문에 생기는 동일한 특성이며, 이번 추가 기능에서
 * 새로 만든 문제는 아니다. 구매 시점 단가를 정확히 보존하려면 OrderItem에 필드를 추가하는
 * 스키마 변경이 필요하므로, "기존 로직 유지" 요청에 따라 이번 범위에서는 다루지 않는다.
 */
@Service
@RequiredArgsConstructor
public class PromotionService {

    private final ProductRepository productRepository;
    private final CustomerRepository customerRepository;
    private final OrderItemRepository orderItemRepository;
    private final ProductDiscountRepository discountRepository;
    private final FlashSaleEventRepository eventRepository;
    private final EventParticipationRepository participationRepository;
    private final SessionHandler sessionHandler;

    // =====================================================================
    // 특별할인 (Special Discount)
    // =====================================================================

    /** 상품에 기간 한정 할인 등록 (관리자용 - 별도 인증은 이번 범위에서는 두지 않음) */
    public Response createDiscount(Long productId, Double discountRate,
                                    LocalDateTime startAt, LocalDateTime endAt) {
        if (productId == null || discountRate == null || discountRate <= 0 || discountRate >= 1
                || startAt == null || endAt == null || !startAt.isBefore(endAt)) {
            throw new ParameterException("productId", "discountRate", "startAt", "endAt");
        }

        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        ProductDiscount discount = new ProductDiscount(product, discountRate, startAt, endAt);
        return new Response(discountRepository.save(discount));
    }

    /** 상품의 현재 할인 적용 여부 및 할인가 조회 */
    public Response getActiveDiscount(Long productId) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        Optional<ProductDiscount> discount =
                discountRepository.findActiveDiscount(productId, LocalDateTime.now());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("productId", product.getId());
        result.put("productName", product.getProductName());
        result.put("originalPrice", product.getProductPrice());

        if (discount.isEmpty()) {
            result.put("discountActive", false);
            result.put("discountedPrice", product.getProductPrice());
        } else {
            result.put("discountActive", true);
            result.put("discountRate", discount.get().getDiscountRate());
            result.put("discountedPrice", discount.get().applyDiscount(product.getProductPrice()));
        }
        return new Response(result);
    }

    /**
     * 할인가로 상품 주문 (로그인 필요)
     * - 기존 CustomerService.placeOrder와 별개의 메서드이며, 정상가 주문 로직에는 영향 없음
     * - 유효한 할인이 없으면 DISCOUNT_NOT_AVAILABLE
     */
    @Transactional
    public Response placeDiscountOrder(OrderRequest order) {
        if (order.getProductId() == null || order.getQuantity() == null || order.getQuantity() <= 0) {
            throw new ParameterException("productId", "quantity");
        }

        String customerId = sessionHandler.getCurrentCustomerId();

        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));
        Product product = productRepository.findById(order.getProductId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        ProductDiscount discount = discountRepository
                .findActiveDiscount(product.getId(), LocalDateTime.now())
                .orElseThrow(() -> new ResponseException(Error.DISCOUNT_NOT_AVAILABLE, "적용 가능한 할인이 없습니다."));

        double unitPrice = discount.applyDiscount(product.getProductPrice());
        double totalPrice = unitPrice * order.getQuantity();

        if (customer.getCustomerPoint() < totalPrice) {
            throw new ResponseException(Error.INSUFFICIENT_FUNDS, "포인트가 부족합니다.");
        }

        customer.setCustomerPoint(customer.getCustomerPoint() - totalPrice);

        // 기존 OrderItem을 그대로 재사용 - 같은 상품 재주문 시 수량 누적 규칙도 동일하게 적용
        Optional<OrderItem> existingItem = orderItemRepository.findByCustomerAndProduct(customer, product);
        if (existingItem.isPresent()) {
            OrderItem item = existingItem.get();
            item.setQuantity(item.getQuantity() + order.getQuantity());
            orderItemRepository.save(item);
        } else {
            orderItemRepository.save(new OrderItem(customer, product, order.getQuantity()));
        }

        customerRepository.save(customer);

        return new Response(String.format(
                "할인 주문이 완료되었습니다. 정가: %.0f, 할인단가: %.0f, 남은 포인트: %.0f",
                product.getProductPrice(), unitPrice, customer.getCustomerPoint()));
    }

    // =====================================================================
    // 선착순 이벤트 (Flash Sale Event)
    // =====================================================================

    /** 선착순 이벤트 등록 (관리자용) */
    public Response createEvent(Long productId, Double eventPrice, Integer totalQuantity,
                                 LocalDateTime startAt, LocalDateTime endAt) {
        if (productId == null || eventPrice == null || eventPrice <= 0
                || totalQuantity == null || totalQuantity <= 0
                || startAt == null || endAt == null || !startAt.isBefore(endAt)) {
            throw new ParameterException("productId", "eventPrice", "totalQuantity", "startAt", "endAt");
        }

        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        FlashSaleEvent event = new FlashSaleEvent(product, eventPrice, totalQuantity, startAt, endAt);
        return new Response(eventRepository.save(event));
    }

    /** 이벤트 상세(잔여 수량 포함) 조회 */
    public Response getEvent(Long eventId) {
        FlashSaleEvent event = eventRepository.findById(eventId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "이벤트를 찾을 수 없습니다."));
        return new Response(event);
    }

    /**
     * 선착순 이벤트 참여(=이벤트가로 주문) - 로그인 필요
     *
     * 처리 순서가 중요하다:
     * 1) 이벤트 유효성(기간/활성화) 확인
     * 2) 중복 참여 여부 확인(1차 방어)
     * 3) 잔여 수량 원자적 차감 (조건부 UPDATE) - 이 트랜잭션의 핵심 동시성 제어 지점
     * 4) 포인트 검증 및 차감
     * 5) OrderItem 반영 + 참여 이력 저장(2차 방어 - DB 유니크 제약)
     *
     * 이 메서드 전체가 @Transactional 이므로, 어느 단계에서든 예외가 발생하면
     * 그 안에서 실행된 모든 변경(수량 차감 포함)이 자동으로 롤백된다.
     * 따라서 "실패 시 수량을 수동으로 복구"하는 보정 코드가 별도로 필요하지 않다.
     */
    @Transactional
    public Response joinFlashSaleEvent(Long eventId, Integer quantity) {
        if (eventId == null || quantity == null || quantity <= 0) {
            throw new ParameterException("eventId", "quantity");
        }

        String customerId = sessionHandler.getCurrentCustomerId();
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));

        FlashSaleEvent event = eventRepository.findById(eventId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "이벤트를 찾을 수 없습니다."));

        LocalDateTime now = LocalDateTime.now();
        if (!event.isValidAt(now)) {
            throw new ResponseException(Error.EVENT_NOT_AVAILABLE, "진행 중인 이벤트가 아닙니다.");
        }

        if (participationRepository.existsByEventAndCustomer(event, customer)) {
            throw new ResponseException(Error.EVENT_ALREADY_PARTICIPATED, "이미 참여한 이벤트입니다.");
        }

        // ---- 선착순 수량 원자적 차감 (동시 요청에도 초과 판매되지 않도록 하는 핵심 로직) ----
        int updated = eventRepository.decrementIfAvailable(eventId, quantity);
        if (updated == 0) {
            throw new ResponseException(Error.EVENT_SOLD_OUT, "선착순 수량이 모두 소진되었습니다.");
        }

        double totalPrice = event.getEventPrice() * quantity;
        if (customer.getCustomerPoint() < totalPrice) {
            // 이 예외로 트랜잭션이 롤백되며 위에서 차감한 수량도 자동으로 원복된다.
            throw new ResponseException(Error.INSUFFICIENT_FUNDS, "포인트가 부족합니다.");
        }

        customer.setCustomerPoint(customer.getCustomerPoint() - totalPrice);
        customerRepository.save(customer);

        Product product = event.getProduct();
        Optional<OrderItem> existingItem = orderItemRepository.findByCustomerAndProduct(customer, product);
        if (existingItem.isPresent()) {
            OrderItem item = existingItem.get();
            item.setQuantity(item.getQuantity() + quantity);
            orderItemRepository.save(item);
        } else {
            orderItemRepository.save(new OrderItem(customer, product, quantity));
        }

        // 참여 이력 저장 - 유니크 제약 위반 시(동시 중복 참여) 예외가 발생하며 트랜잭션 전체가 롤백된다.
        participationRepository.save(new EventParticipation(event, customer));

        return new Response(String.format(
                "이벤트 참여가 완료되었습니다. 이벤트단가: %.0f, 남은 포인트: %.0f",
                event.getEventPrice(), customer.getCustomerPoint()));
    }
}
