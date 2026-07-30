package com.skala.stock.service;

import com.skala.stock.dto.UserDto;
import com.skala.stock.entity.User;
import com.skala.stock.repository.UserRepository;
import lombok.RequiredArgsConstructor;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;


@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;

    @Transactional
    public UserDto createUser(UserDto userDto) {
        if (userRepository.existsByUsername(userDto.getUsername())) {
            throw new RuntimeException("이미 존재하는 사용자명입니다: " + userDto.getUsername());
        }
        if (userRepository.existsByEmail(userDto.getEmail())) {
            throw new RuntimeException("이미 존재하는 이메일입니다: " + userDto.getEmail());
        }

        User user = User.builder()
                .username(userDto.getUsername())
                .password(userDto.getPassword())
                .email(userDto.getEmail())
                .balance(userDto.getBalance())
                .build();

        User savedUser = userRepository.save(user);
        return convertToDto(savedUser);
    }

    public UserDto getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다: " + id));
        return convertToDto(user);
    }

    // User Get 조회 함수 (기존 findALL 내장 메서드 활용) 
    // Why? Query문을 활용할 만큼 복잡한 것이 아니고 내장 메서드를 활용해도 충분히 가능하기 때문
    public List<UserDto> getAllUsers() {
            return userRepository.findAll().stream()
                    .map(this::convertToDto)
                    .collect(Collectors.toList());
    }
    // User DELETE (기존 deleteById 내장 메서드 활용)
    // Why? Query문을 활용할 만큼 복잡한 것이 아니고 내장 메서드를 활용해도 충분히 가능하기 때문
    @Transactional
    public void deleteUser(Long id) {
            if (!userRepository.existsById(id)) {
                throw new RuntimeException("삭제할 사용자를 찾을 수 없습니다: " + id);
            }
            userRepository.deleteById(id);
        }
    
    private UserDto convertToDto(User user) {
        return UserDto.builder()
                .id(user.getId())
                .username(user.getUsername())
                .password(user.getPassword())
                .email(user.getEmail())
                .balance(user.getBalance())
                .build();
    }
}
