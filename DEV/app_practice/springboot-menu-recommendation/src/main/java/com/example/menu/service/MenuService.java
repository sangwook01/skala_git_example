package com.example.menu.service;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 메뉴 추천 비즈니스 로직을 담당하는 Spring Bean입니다.
 *
 * @Service를 사용하면 Component Scan을 통해 Spring Container에
 * 자동으로 Bean으로 등록됩니다.
 */
@Service
public class MenuService {

    private final List<String> menus = List.of(
            "김치찌개",
            "불고기",
            "짜장면",
            "돈가스",
            "떡볶이",
            "치킨",
            "피자",
            "국밥" // 국밥 추가하기
    );

    public String recommend() {
        return "김치찌개";
    }

    public String recommendByCategory(String category) {
        return switch (category) {
            case "korean" -> "불고기";
            case "chinese" -> "짜장면";
            case "japanese" -> "돈가스";
            case "snack" -> "떡볶이";
            default -> "추천 가능한 메뉴가 없습니다";
        };
    }

    public String randomMenu() {
        int index = ThreadLocalRandom.current().nextInt(menus.size());
        return menus.get(index);
    }

 // 날씨별 랜덤 추천 (weather 조건은 고정, 내부 메뉴만 랜덤)
    public String recommendByWeather(String weather) {
        List<String> list = switch (weather) {
            case "sunny" -> List.of("샌드위치", "김밥", "수제버거", "파스타");
            case "rainy" -> List.of("해물파전", "칼국수", "수제비", "짬뽕");
            case "hot"   -> List.of("물냉면", "콩국수", "빙수", "메밀소바");
            case "cold"  -> List.of("부대찌개", "훠궈", "어묵탕", "갈비탕");
            default      -> List.of();
        };

        if (list.isEmpty()) {
            return "추천 가능한 메뉴가 없습니다";
        }
        
        int index = ThreadLocalRandom.current().nextInt(list.size());
        return list.get(index);
    }

    // 기분별 랜덤 추천 (mood 조건은 고정, 내부 메뉴만 랜덤)
    public String recommendByMood(String mood) {
        List<String> list = switch (mood) {
            case "happy"     -> List.of("치킨", "피자", "아이스크림", "스테이크");
            case "sad"       -> List.of("매운 떡볶이", "초콜릿", "마라탕", "우동");
            case "tired"     -> List.of("삼계탕", "장어구이", "전복죽", "고기덮밥");
            case "stressed"  -> List.of("매운 닭발", "불족발", "불닭볶음면", "매운 짬뽕");
            default          -> List.of("달콤한 디저트");
        };

        int index = ThreadLocalRandom.current().nextInt(list.size());
        return list.get(index);
    }

    // 가격대별 랜덤 추천 (가격 구간 내 메뉴들 중 랜덤)
    public String recommendByPrice(int min, int max) {
        if (min > max) {
            return "최소 가격이 최대 가격보다 클 수 없습니다.";
        }

        List<String> list;
        if (max <= 6000) {
            list = List.of("삼각김밥 & 라면", "한솥 도시락", "편의점 샌드위치", "토스트");
        } else if (max <= 12000) {
            list = List.of("제육덮밥", "순대국밥", "짜장면", "돈가스", "김치찌개");
        } else {
            list = List.of("소고기 스테이크", "초밥 정식", "양갈비", "코스 요리");
        }

        int index = ThreadLocalRandom.current().nextInt(list.size());
        return list.get(index);
    }

    // 나만의 추천 (혼밥 메뉴 목록 중 랜덤)
    public String recommendCustom(String companion, String time, String season) {
            List<String> list;

            // 1. 남은 시간이 10분으로 매우 짧은 경우 (누구와 함께든 빠르게 먹는 간편식)
            if ("10min".equals(time)) {
                list = switch (companion) {
                    case "family", "friends" -> List.of("패스트푸드 햄버거 세트", "길거리 핫도그 & 떡볶이", "스탠딩 타코");
                    default                  -> List.of("편의점 삼각김밥 & 라면", "이삭토스트", "바나나 & 유청단백질");
                };
            } 
            // 2. 가족과 함께 먹는 경우
            else if ("family".equals(companion)) {
                list = switch (season) {
                    case "summer" -> List.of("한방 삼계탕", "몸보신 오리백숙", "해물 물회 정식");
                    case "winter" -> List.of("소갈비찜 정식", "해물탕 & 볶음밥", "만두전골");
                    default       -> List.of("패밀리 레스토랑 스테이크", "한정식 코스", "킹크랩 구이");
                };
            } 
            // 3. 친구들과 함께 먹는 경우
            else if ("friends".equals(companion)) {
                list = switch (season) {
                    case "summer" -> List.of("야외 야장 솥뚜껑 삼겹살", "치맥 정식", "시원한 김치말이국수 & 편육");
                    case "winter" -> List.of("마라탕 & 꿔바로우", "곱창전골", "모둠 조개구이");
                    default       -> List.of("화덕 피자 & 파스타", "족발 & 보쌈 세트", "수제버거 & 맥주");
                };
            } 
            // 4. 혼자 먹는 경우 (혼밥 특화)
            else {
                list = switch (season) {
                    case "summer" -> List.of("살얼음 물냉면", "초계국수", "일식 자루소바");
                    case "winter" -> List.of("1인 얼큰 국밥", "돈코츠 라멘", "1인 보쌈 정식");
                    case "autumn" -> List.of("추어탕 정식", "연어 덮밥(사케동)", "버섯 들깨수제비");
                    default       -> List.of("치즈 돈가스", "제육볶음 정식", "카레라이스");
                };
            }

            int index = ThreadLocalRandom.current().nextInt(list.size());
            return list.get(index);
        }
    }