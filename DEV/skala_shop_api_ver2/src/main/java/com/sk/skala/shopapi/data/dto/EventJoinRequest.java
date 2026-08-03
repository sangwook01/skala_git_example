package com.sk.skala.shopapi.data.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * [추가 기능] 선착순 이벤트 참여 요청 DTO (POST /api/promotions/events/{eventId}/join)
 * eventId는 경로변수로 받으므로 body에는 수량만 담는다.
 */
@Getter
@Setter
@NoArgsConstructor
public class EventJoinRequest {

    private Integer quantity;
}
