package com.sk.skala.shopapi.data.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 상품 주문(POST /api/customers/order) / 주문 취소(POST /api/customers/cancel) 요청 DTO
 */
@Getter
@Setter
@NoArgsConstructor
public class OrderRequest {

    private Long productId;
    private Integer quantity;
}
