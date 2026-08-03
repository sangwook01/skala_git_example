package com.sk.skala.shopapi.data.table;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 고객(Customer) 엔터티 - ID는 문자열 customerId를 그대로 사용
 */
@Entity
@Table(name = "customer")
@Getter
@Setter
@NoArgsConstructor
public class Customer {

    @Id
    private String customerId;

    @Column(nullable = false)
    private String customerPassword;

    @Column(nullable = false)
    private Double customerPoint;

    public Customer(String customerId, Double customerPoint) {
        this.customerId = customerId;
        this.customerPoint = customerPoint;
    }
}
