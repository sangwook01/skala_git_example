package com.sk.skala.shopapi.tools;

/**
 * 문자열 관련 유틸리티 (필수값 검증 등)
 */
public class StringUtil {

    private StringUtil() {
    }

    public static boolean isEmpty(String value) {
        return value == null || value.trim().isEmpty();
    }

    public static boolean isAnyEmpty(String... values) {
        for (String value : values) {
            if (isEmpty(value)) {
                return true;
            }
        }
        return false;
    }
}
