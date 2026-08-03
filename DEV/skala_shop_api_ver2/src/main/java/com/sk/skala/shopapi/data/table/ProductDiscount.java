package com.sk.skala.shopapi.data.table;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

/**
 * [추가 기능] 특별할인(Special Discount) 엔터티
 *
 * 기존 Product/Customer/OrderItem 도메인은 전혀 건드리지 않고,
 * 특정 상품에 "기간 한정 할인율"을 별도로 걸어두기 위한 독립 테이블이다.
 * 실제 할인 주문은 PromotionService.placeDiscountOrder 에서만 이 정보를 참조하며,
 * 기존 /api/customers/order (정상가 주문) 로직에는 전혀 영향을 주지 않는다.
 */
@Entity
@Table(name = "product_discount")
@Getter
@Setter
@NoArgsConstructor
public class ProductDiscount {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    /** 할인율 (0.0 초과 1.0 미만, 예: 0.2 = 20% 할인) */
    @Column(nullable = false)
    private Double discountRate;

    @Column(nullable = false)
    private LocalDateTime startAt;

    @Column(nullable = false)
    private LocalDateTime endAt;

    /** 관리자가 기간이 남았어도 즉시 중단할 수 있도록 하는 스위치 */
    @Column(nullable = false)
    private Boolean active = true;

    public ProductDiscount(Product product, Double discountRate, LocalDateTime startAt, LocalDateTime endAt) {
        this.product = product;
        this.discountRate = discountRate;
        this.startAt = startAt;
        this.endAt = endAt;
        this.active = true;
    }

    /** 지금 이 시각에 이 할인이 유효한지(active + 기간 내) 판단 */
    public boolean isValidAt(LocalDateTime now) {
        return Boolean.TRUE.equals(active) && !now.isBefore(startAt) && !now.isAfter(endAt);
    }

    /** 원가에 할인율을 적용한 판매가 계산 */
    public double applyDiscount(double originalPrice) {
        return originalPrice * (1 - discountRate);
    }
}
