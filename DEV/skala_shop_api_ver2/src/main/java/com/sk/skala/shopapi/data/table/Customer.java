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
 *
 * [추가] customerName - API 목록 표의 "GET ~/api/customers/{customerName}
 * (Name에 해당하는 고객 상세 정보)" 항목을 지원하기 위해 추가한 선택(nullable) 필드.
 * 원래 실습 명세(1-2 엔터티 설계)에는 없던 필드이지만, API 목록 표에 이름 조회 기능이
 * 명시되어 있어 이를 실제로 구현하기 위해 추가했다. 회원가입 시 필수는 아니며,
 * 값을 지정하지 않으면 null로 남는다. 이름으로 조회가 가능하려면 값이 유일해야 하므로
 * unique 제약을 걸어둔다(단, null 값은 여러 개 허용됨 - 표준 SQL의 유니크 제약 규칙).
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

    @Column(unique = true)
    private String customerName;

    public Customer(String customerId, Double customerPoint) {
        this.customerId = customerId;
        this.customerPoint = customerPoint;
    }
}
