package com.sk.skala.shopapi.controller;

import com.sk.skala.shopapi.common.Response;
import com.sk.skala.shopapi.data.dto.DiscountRequest;
import com.sk.skala.shopapi.data.dto.EventJoinRequest;
import com.sk.skala.shopapi.data.dto.EventRequest;
import com.sk.skala.shopapi.data.dto.OrderRequest;
import com.sk.skala.shopapi.service.PromotionService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * [추가 기능] 특별할인 / 선착순 이벤트 API
 * 기존 ProductController, CustomerController와 완전히 분리된 신규 컨트롤러.
 */
@RestController
@RequestMapping("/api/promotions")
@RequiredArgsConstructor
public class PromotionController {

    private final PromotionService promotionService;

    // ---------------- 특별할인 ----------------

    /** 상품에 기간 한정 할인 등록 (관리자용) */
    @PostMapping("/discounts")
    public Response createDiscount(@RequestBody DiscountRequest request) {
        return promotionService.createDiscount(
                request.getProductId(), request.getDiscountRate(),
                request.getStartAt(), request.getEndAt());
    }

    /** 상품의 현재 할인 적용 여부 및 할인가 조회 */
    @GetMapping("/discounts/{productId}")
    public Response getActiveDiscount(@PathVariable Long productId) {
        return promotionService.getActiveDiscount(productId);
    }

    /** 할인가로 상품 주문 (로그인 필요) */
    @PostMapping("/discounts/order")
    public Response placeDiscountOrder(@RequestBody OrderRequest order) {
        return promotionService.placeDiscountOrder(order);
    }

    // ---------------- 선착순 이벤트 ----------------

    /** 선착순 이벤트 등록 (관리자용) */
    @PostMapping("/events")
    public Response createEvent(@RequestBody EventRequest request) {
        return promotionService.createEvent(
                request.getProductId(), request.getEventPrice(), request.getTotalQuantity(),
                request.getStartAt(), request.getEndAt());
    }

    /** 이벤트 상세(잔여 수량 포함) 조회 */
    @GetMapping("/events/{eventId}")
    public Response getEvent(@PathVariable Long eventId) {
        return promotionService.getEvent(eventId);
    }

    /** 선착순 이벤트 참여 (이벤트가로 주문, 로그인 필요) */
    @PostMapping("/events/{eventId}/join")
    public Response joinEvent(@PathVariable Long eventId, @RequestBody EventJoinRequest request) {
        return promotionService.joinFlashSaleEvent(eventId, request.getQuantity());
    }
}
