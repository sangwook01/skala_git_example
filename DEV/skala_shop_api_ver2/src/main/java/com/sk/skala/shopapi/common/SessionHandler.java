package com.sk.skala.shopapi.common;

import com.sk.skala.shopapi.exception.Error;
import com.sk.skala.shopapi.exception.ResponseException;
import com.sk.skala.shopapi.tools.JwtUtil;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * 로그인 성공 시 JWT를 쿠키(bff-access)로 발급하고,
 * 이후 요청에서 쿠키의 JWT를 검증해 로그인된 고객을 식별하는 컴포넌트
 */
@Component
@RequiredArgsConstructor
public class SessionHandler {

    private static final String COOKIE_NAME = "bff-access";

    private final JwtUtil jwtUtil;

    /**
     * 로그인 성공 시 JWT를 생성해 Cookie(Set-Cookie: bff-access=&lt;JWT&gt;)로 내려줌
     */
    public void storeAccessToken(String customerId, HttpServletResponse response) {
        String token = jwtUtil.generateToken(customerId);

        Cookie cookie = new Cookie(COOKIE_NAME, token);
        cookie.setHttpOnly(true);
        cookie.setPath("/");
        cookie.setMaxAge(60 * 60); // 1시간
        response.addCookie(cookie);
    }

    /**
     * 현재 요청의 Cookie에서 JWT를 추출해 검증 후 로그인된 customerId를 반환
     * - 쿠키 자체가 없으면 "로그인 필요"(UNAUTHORIZED)
     * - 쿠키는 있지만 서명이 틀리거나 만료된 경우 "인증 실패"(NOT_AUTHENTICATED)로 구분
     */
    public String getCurrentCustomerId() {
        HttpServletRequest request = getCurrentRequest();
        Cookie[] cookies = request.getCookies();

        if (cookies == null) {
            throw new ResponseException(Error.UNAUTHORIZED, "로그인이 필요합니다.");
        }

        for (Cookie cookie : cookies) {
            if (COOKIE_NAME.equals(cookie.getName())) {
                String token = cookie.getValue();
                if (!jwtUtil.isValid(token)) {
                    throw new ResponseException(Error.NOT_AUTHENTICATED, "유효하지 않거나 만료된 토큰입니다.");
                }
                return jwtUtil.extractCustomerId(token);
            }
        }

        throw new ResponseException(Error.UNAUTHORIZED, "로그인이 필요합니다.");
    }

    private HttpServletRequest getCurrentRequest() {
        ServletRequestAttributes attributes =
                (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();

        if (attributes == null) {
            throw new ResponseException(Error.UNAUTHORIZED, "요청 컨텍스트를 찾을 수 없습니다.");
        }
        return attributes.getRequest();
    }
}
