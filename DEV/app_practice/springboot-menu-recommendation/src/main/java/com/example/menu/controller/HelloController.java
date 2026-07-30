package com.example.menu.controller; 
import com.example.menu.service.HelloService;
import com.example.menu.dto.HelloResponse;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
@RestController
public class HelloController {
    private final HelloService helloService;
    // 생성자 주입
    public HelloController(HelloService helloService) {
        this.helloService = helloService;
    }
    @GetMapping("/hello")
    public HelloResponse hello(@RequestParam(defaultValue = "SKALA") String name) {
    // 서비스 호출하여 응답 객체 생성
        return helloService.createMessage(name);
    }
}