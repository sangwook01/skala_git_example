package com.sk.skala.shopapi.data.table;

import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * [추가 기능] 선착순 이벤트 참여 이력 엔터티
 *
 * "1인 1회" 제한을 위한 기록. (event_id, customer_id) 조합에 유니크 제약을 걸어
 * 서비스 계층의 사전 확인(existsByEventAndCustomer)이 동시성 상황에서 뚫리더라도
 * DB 레벨에서 최종적으로 중복 참여를 막아준다(제약 위반 시 저장이 실패하고,
 * 같은 트랜잭션 안의 포인트 차감·수량 차감도 함께 롤백된다).
 */
@Entity
@Table(name = "event_participation",
        uniqueConstraints = @UniqueConstraint(name = "uk_event_customer", columnNames = {"event_id", "customer_id"}))
@Getter
@Setter
@NoArgsConstructor
public class EventParticipation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "event_id", nullable = false)
    private FlashSaleEvent event;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    public EventParticipation(FlashSaleEvent event, Customer customer) {
        this.event = event;
        this.customer = customer;
    }
}
