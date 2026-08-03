package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.Customer;
import com.sk.skala.shopapi.data.table.EventParticipation;
import com.sk.skala.shopapi.data.table.FlashSaleEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EventParticipationRepository extends JpaRepository<EventParticipation, Long> {

    /** 해당 고객이 해당 이벤트에 이미 참여했는지 확인 (1인 1회 제한의 1차 방어선) */
    boolean existsByEventAndCustomer(FlashSaleEvent event, Customer customer);
}
