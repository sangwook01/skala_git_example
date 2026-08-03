package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.FlashSaleEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface FlashSaleEventRepository extends JpaRepository<FlashSaleEvent, Long> {

    /**
     * [선착순 핵심 로직] 잔여 수량을 "조건부로" 원자적으로 차감한다.
     *
     * 잘못된 방식 (동시성 버그 발생):
     *   FlashSaleEvent e = repo.findById(id);
     *   if (e.getRemainingQuantity() >= qty) {
     *       e.setRemainingQuantity(e.getRemainingQuantity() - qty);
     *       repo.save(e);
     *   }
     *   -> 두 트랜잭션이 동시에 같은 값을 읽으면(예: 남은 수량 1) 둘 다 "충분하다"고 판단해
     *      실제로는 1개만 남았는데 2명에게 판매되는 초과 판매(overselling)가 발생한다.
     *
     * 올바른 방식 (이 메서드):
     *   UPDATE ... SET remaining = remaining - :qty WHERE id = :id AND remaining >= :qty
     *   -> "읽고 판단하고 쓰는" 것이 하나의 SQL 문으로 원자적으로 처리되어,
     *      동시에 여러 요청이 와도 DB가 순차적으로 처리하며 조건을 만족하는 요청만 성공한다.
     *
     * @return 실제로 갱신된 row 수. 0이면 잔여 수량 부족(품절)으로 판단한다.
     */
    @Modifying(clearAutomatically = true)
    @Query("update FlashSaleEvent f set f.remainingQuantity = f.remainingQuantity - :qty " +
           "where f.id = :id and f.remainingQuantity >= :qty")
    int decrementIfAvailable(@Param("id") Long id, @Param("qty") int qty);
}
