package com.sk.skala.shopapi.exception;

import com.sk.skala.shopapi.common.Response;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 컨트롤러 전역에서 발생하는 예외를 일괄 처리하여
 * 일관된 형식의 에러 응답(Response)으로 변환
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResponseException.class)
    public ResponseEntity<Response> handleResponseException(ResponseException e) {
        log.warn("ResponseException [{}]: {}", e.getError().getCode(), e.getMessage());
        Error error = e.getError();
        Response response = new Response(error.getStatus(),
                e.getMessage() != null ? e.getMessage() : error.getMessage());
        return ResponseEntity.status(error.getStatus()).body(response);
    }

    @ExceptionHandler(ParameterException.class)
    public ResponseEntity<Response> handleParameterException(ParameterException e) {
        log.warn("ParameterException: {}", e.getMessage());
        Response response = new Response(HttpStatus.BAD_REQUEST.value(), e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Response> handleException(Exception e) {
        log.error("예상하지 못한 서버 오류", e);
        Response response = new Response(HttpStatus.INTERNAL_SERVER_ERROR.value(), "서버 내부 오류가 발생했습니다.");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}
