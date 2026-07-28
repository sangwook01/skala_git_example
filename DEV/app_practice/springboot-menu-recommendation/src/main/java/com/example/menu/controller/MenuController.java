package com.example.menu.controller;

import com.example.menu.dto.MenuResponse;
import com.example.menu.service.MenuService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestParam; // RequestParam을 사용하기 위해 import를 추가해주어야됨

/**
 * 브라우저의 HTTP 요청을 받아 메뉴 추천 결과를 반환한다.
 */
@RestController
@RequestMapping("/api")
public class MenuController {

    private final MenuService menuService;

    /**
     * Spring Container가 MenuService Bean을 생성자에 주입합니다.
     */
    public MenuController(MenuService menuService) {
        this.menuService = menuService;
    }

    @GetMapping("/hello/{name}")
    public String hello(@PathVariable("name") String name) {
        return name + "님, 오늘도 맛있는 하루 보내세요!";
    }

    @GetMapping("/menu")
    public String menu() {
        return "오늘의 추천 메뉴는 " + menuService.recommend() + "입니다.";
    }

    @GetMapping("/menu/random")
    public String randomMenu() {
        return "오늘은 " + menuService.randomMenu() + " 어떠세요?";
    }
/* 
    @GetMapping("/menu/{category}")
    public String menuByCategory(@PathVariable("category") String category) {
        String menu = menuService.recommendByCategory(category);
        return category + " 추천 메뉴는 " + menu + "입니다.";
    }
*/
    @GetMapping("/menu/json/{category}")
    public MenuResponse menuJson(@PathVariable("category") String category) {
        String menu = menuService.recommendByCategory(category);

        return new MenuResponse(
                category,
                menu,
                "오늘은 " + menu + " 어떠세요?"
        );
    }
// 날씨별 추천 (GET /api/menu/weather/{weather})
    // -> String 반환 방식 (과제 힌트: menuByCategory 구조)
    @GetMapping("/menu/weather/{weather}")
    public String menuByWeather(@PathVariable("weather") String weather) {
        String menu = menuService.recommendByWeather(weather);
        return weather + " 날씨 추천 메뉴는 " + menu + "입니다.";
    }

// 기분별 추천 (GET /api/menu/mood/{mood})
    // -> MenuResponse (JSON) 반환 방식 (과제 힌트: menuJson 구조)
    @GetMapping("/menu/mood/{mood}")
    public MenuResponse menuByMood(@PathVariable("mood") String mood) {
        String menu = menuService.recommendByMood(mood);
        return new MenuResponse(
                mood,
                menu,
                "기분이 " + mood + "할 때는 " + menu + " 어떠세요?"
        );
    }

// 가격대별 추천 (GET /api/menu/price/search?min=5000&max=10000)
    // -> @RequestParam 사용
    @GetMapping("/menu/price/search")
    public String menuByPrice(@RequestParam("min") int min, @RequestParam("max") int max) {
        return menuService.recommendByPrice(min, max);
    }

// 나만의 추천 (GET /api/menu/my/solo)
    @GetMapping("/menu/my/custom")
        public MenuResponse menuCustom(
                @RequestParam(value = "companion", defaultValue = "solo") String companion,
                @RequestParam(value = "time", defaultValue = "30min") String time,
                @RequestParam(value = "season", defaultValue = "spring") String season) {
            
            String menu = menuService.recommendCustom(companion, time, season);
            
            // 보기 쉽게 한국어 조합으로 가공하여 반환
            String customSummary = String.format("[%s / %s / %s]", companion, time, season);
            return new MenuResponse(
                    customSummary,
                    menu,
                    "선택하신 조건에 맞춘 완벽한 맞춤 추천 메뉴입니다!"
            );
        }
    // 범용 가변 경로인 /menu/{category}를 맨 아래로 이동 필요
    @GetMapping("/menu/{category}")
    public String menuByCategory(@PathVariable("category") String category) {
        String menu = menuService.recommendByCategory(category);
        return category + " 추천 메뉴는 " + menu + "입니다.";
    }
}