package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.Product;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Long> {

    /**
     * 상품명과 동일한 상품이 존재하는지 조회 (중복 등록 방지 목적)
     * 메서드 이름만으로 쿼리가 생성되는 Query Method
     */
    Optional<Product> findByProductName(String productName);
}
