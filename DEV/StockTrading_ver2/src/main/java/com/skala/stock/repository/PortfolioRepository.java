package com.skala.stock.repository;

import com.skala.stock.entity.Portfolio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

@Repository
public interface PortfolioRepository extends JpaRepository<Portfolio, Long> {
    List<Portfolio> findByUserId(Long userId);
    Optional<Portfolio> findByUserIdAndStockId(Long userId, Long stockId);
    boolean existsByUserIdAndStockId(Long userId, Long stockId);

    // @Query를 사용한 특정 주식 보유 현황 조회
    @Query("SELECT p FROM Portfolio p WHERE p.user.id = :userId AND p.stock.id = :stockId")
    Optional<Portfolio> findByUserIdAndStockIdWithQuery(@Param("userId") Long userId, @Param("stockId") Long stockId);
}
