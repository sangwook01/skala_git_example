package com.example.menu.service;
import com.example.menu.dto.HelloResponse;
import org.springframework.stereotype.Service;

    @Service
    public class HelloService {
        public HelloResponse createMessage(String name) {
            HelloResponse response = new HelloResponse();
            response.setMessage("안녕하세요, " + name + "님!");
            return response;
        }
    }