package com.sk.skala.shopapi.data.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

/**
 * [추가 기능] 특별할인 등록 요청 DTO (POST /api/promotions/discounts)
 */
@Getter
@Setter
@NoArgsConstructor
public class DiscountRequest {

    private Long productId;

    /** 0.0 초과 1.0 미만 (예: 0.2 = 20% 할인) */
    private Double discountRate;

    private LocalDateTime startAt;
    private LocalDateTime endAt;
}
