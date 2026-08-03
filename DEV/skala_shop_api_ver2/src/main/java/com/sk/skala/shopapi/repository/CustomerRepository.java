package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.Customer;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

/**
 * Customer 엔터티 저장소
 */
public interface CustomerRepository extends JpaRepository<Customer, String> {

    /**
     * customerName으로 고객 조회 (GET /api/customers/{customerName} 지원용)
     * Query Method - 메서드 이름만으로 쿼리가 생성됨
     */
    Optional<Customer> findByCustomerName(String customerName);
}
