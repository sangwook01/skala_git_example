package com.sk.skala.shopapi.exception;

import lombok.Getter;

/**
 * 전역적으로 사용하는 비즈니스 에러 코드 정의
 */
@Getter
public enum Error {

    DATA_NOT_FOUND(404, "DATA_NOT_FOUND", "요청한 데이터를 찾을 수 없습니다."),
    DATA_DUPLICATED(409, "DATA_DUPLICATED", "이미 존재하는 데이터입니다."),
    INSUFFICIENT_FUNDS(400, "INSUFFICIENT_FUNDS", "포인트가 부족합니다."),
    INSUFFICIENT_QUANTITY(400, "INSUFFICIENT_QUANTITY", "취소할 수량이 보유 수량보다 많습니다."),
    NOT_AUTHENTICATED(401, "NOT_AUTHENTICATED", "인증에 실패했습니다."),
    UNAUTHORIZED(401, "UNAUTHORIZED", "로그인이 필요합니다.");

    private final int status;
    private final String code;
    private final String message;

    Error(int status, String code, String message) {
        this.status = status;
        this.code = code;
        this.message = message;
    }
}
