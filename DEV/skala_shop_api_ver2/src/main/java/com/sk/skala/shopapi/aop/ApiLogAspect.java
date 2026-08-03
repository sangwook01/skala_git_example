package com.sk.skala.shopapi.aop;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.stereotype.Component;

import java.util.Arrays;

/**
 * 모든 Controller의 요청/응답/예외를 공통으로 로깅하는 AOP 클래스
 */
@Slf4j
@Aspect
@Component
public class ApiLogAspect {

    private static final String POINTCUT = "execution(* com.sk.skala.shopapi.controller..*(..))";

    @Before(POINTCUT)
    public void logRequest(JoinPoint joinPoint) {
        log.info(">>> API 호출 : {} 파라미터 : {}",
                joinPoint.getSignature().toShortString(),
                Arrays.toString(joinPoint.getArgs()));
    }

    @AfterReturning(pointcut = POINTCUT, returning = "result")
    public void logResponse(JoinPoint joinPoint, Object result) {
        log.info("<<< API 응답 : {} 결과 : {}",
                joinPoint.getSignature().toShortString(),
                result);
    }

    @AfterThrowing(pointcut = POINTCUT, throwing = "ex")
    public void logException(JoinPoint joinPoint, Throwable ex) {
        log.error("!!! API 예외 : {} 오류 : {}",
                joinPoint.getSignature().toShortString(),
                ex.getMessage());
    }
}
