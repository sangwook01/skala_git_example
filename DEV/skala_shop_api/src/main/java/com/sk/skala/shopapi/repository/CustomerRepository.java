package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.Customer;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Customer 엔터티 저장소 - 별도 사용자 정의 메서드 없이 JpaRepository 기본 기능만 사용
 */
public interface CustomerRepository extends JpaRepository<Customer, String> {
}
