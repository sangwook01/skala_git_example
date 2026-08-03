package com.sk.skala.shopapi.data.dto;

import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.AllArgsConstructor;

/**
 * 고객이 보유(주문)한 상품 정보 - 상품 정보 + 수량
 * Builder 패턴으로 메서드 체이닝 제공
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItemDto {

    private Long productId;
    private String productName;
    private Double productPrice;
    private Integer quantity;
}
