package com.sk.skala.shopapi.exception;

import lombok.Getter;

/**
 * Error enum을 기반으로 한 비즈니스 로직 예외
 * (예: DATA_NOT_FOUND, INSUFFICIENT_FUNDS 등)
 */
@Getter
public class ResponseException extends RuntimeException {

    private final Error error;

    public ResponseException(Error error) {
        super(error.getMessage());
        this.error = error;
    }

    public ResponseException(Error error, String message) {
        super(message);
        this.error = error;
    }
}
