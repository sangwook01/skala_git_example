package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.ProductDiscount;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.Optional;

public interface ProductDiscountRepository extends JpaRepository<ProductDiscount, Long> {

    /**
     * 특정 상품에 대해 "지금 이 시각" 유효한 할인 1건을 조회한다.
     * 같은 상품에 여러 할인이 겹쳐 등록된 경우 가장 최근에 등록된 것을 우선한다(id desc).
     */
    @Query("select d from ProductDiscount d " +
           "where d.product.id = :productId and d.active = true " +
           "and :now between d.startAt and d.endAt " +
           "order by d.id desc")
    Optional<ProductDiscount> findActiveDiscount(@Param("productId") Long productId,
                                                  @Param("now") LocalDateTime now);
}
