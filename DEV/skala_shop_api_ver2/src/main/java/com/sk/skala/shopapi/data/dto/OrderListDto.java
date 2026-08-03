package com.sk.skala.shopapi.data.dto;

import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.AllArgsConstructor;

import java.util.List;

/**
 * 고객이 주문한 상품 목록 조회 응답 DTO
 * Builder 패턴으로 메서드 체이닝 제공
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder

public class OrderListDto {

    private String customerId;
    private Double customerPoint;
    private List<OrderItemDto> products;
}
