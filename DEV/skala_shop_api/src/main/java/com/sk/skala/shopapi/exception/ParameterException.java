package com.sk.skala.shopapi.exception;

import lombok.Getter;

/**
 * 필수 파라미터 누락/유효성 검증 실패 시 발생하는 예외
 */
@Getter
public class ParameterException extends RuntimeException {

    private final String[] parameters;

    public ParameterException(String... parameters) {
        super("필수 파라미터가 누락되었거나 올바르지 않습니다: " + String.join(", ", parameters));
        this.parameters = parameters;
    }
}
