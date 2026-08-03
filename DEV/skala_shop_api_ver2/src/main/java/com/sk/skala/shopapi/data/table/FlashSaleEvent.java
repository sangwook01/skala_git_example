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
 * [추가 기능] 선착순 이벤트(Flash Sale Event) 엔터티
 *
 * 특정 상품을 한정 수량 · 이벤트 특가로 판매하는 이벤트 정보를 담는다.
 * remainingQuantity(잔여 수량)는 반드시 FlashSaleEventRepository.decrementIfAvailable()의
 * "조건부 UPDATE"를 통해서만 차감해야 한다. 엔터티를 읽어서 -1 한 뒤 save 하는 방식은
 * 동시 요청 시 잔여 수량을 잘못 읽어 초과 판매(overselling)로 이어질 수 있으므로 사용하지 않는다.
 */
@Entity
@Table(name = "flash_sale_event")
@Getter
@Setter
@NoArgsConstructor
public class FlashSaleEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    /** 이벤트 특가 (정가와 무관하게 이벤트 전용으로 지정하는 판매가) */
    @Column(nullable = false)
    private Double eventPrice;

    /** 이벤트 시작 시 전체 수량 (기록용) */
    @Column(nullable = false)
    private Integer totalQuantity;

    /** 현재 남은 수량 - 반드시 조건부 UPDATE로만 차감 */
    @Column(nullable = false)
    private Integer remainingQuantity;

    @Column(nullable = false)
    private LocalDateTime startAt;

    @Column(nullable = false)
    private LocalDateTime endAt;

    @Column(nullable = false)
    private Boolean active = true;

    public FlashSaleEvent(Product product, Double eventPrice, Integer totalQuantity,
                           LocalDateTime startAt, LocalDateTime endAt) {
        this.product = product;
        this.eventPrice = eventPrice;
        this.totalQuantity = totalQuantity;
        this.remainingQuantity = totalQuantity;
        this.startAt = startAt;
        this.endAt = endAt;
        this.active = true;
    }

    /** 지금 이 시각에 이 이벤트가 유효한지(active + 기간 내) 판단 */
    public boolean isValidAt(LocalDateTime now) {
        return Boolean.TRUE.equals(active) && !now.isBefore(startAt) && !now.isAfter(endAt);
    }
}
