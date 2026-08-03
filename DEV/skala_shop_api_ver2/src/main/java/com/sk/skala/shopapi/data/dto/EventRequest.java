package com.sk.skala.shopapi.data.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

/**
 * [추가 기능] 선착순 이벤트 등록 요청 DTO (POST /api/promotions/events)
 */
@Getter
@Setter
@NoArgsConstructor
public class EventRequest {

    private Long productId;
    private Double eventPrice;
    private Integer totalQuantity;
    private LocalDateTime startAt;
    private LocalDateTime endAt;
}
