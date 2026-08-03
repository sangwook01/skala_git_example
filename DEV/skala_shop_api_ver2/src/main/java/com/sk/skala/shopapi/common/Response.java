package com.sk.skala.shopapi.common;

import lombok.Getter;
import lombok.Setter;

/**
 * 모든 API가 공통으로 사용하는 응답 래퍼(wrapper) 객체
 */
@Getter
@Setter
public class Response {

    private int status;
    private String message;
    private Object data;

    public Response() {
        this.status = 200;
        this.message = "OK";
    }

    public Response(Object data) {
        this.status = 200;
        this.message = "OK";
        this.data = data;
    }

    public Response(int status, String message) {
        this.status = status;
        this.message = message;
    }

    public Response(int status, String message, Object data) {
        this.status = status;
        this.message = message;
        this.data = data;
    }
}
