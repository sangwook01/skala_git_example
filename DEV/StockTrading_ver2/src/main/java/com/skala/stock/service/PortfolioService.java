package com.skala.stock.service;

import com.skala.stock.dto.PortfolioDto;
import com.skala.stock.entity.Portfolio;
import com.skala.stock.entity.Stock;
import com.skala.stock.repository.PortfolioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PortfolioService {

    private final PortfolioRepository portfolioRepository;

    public List<PortfolioDto> getUserPortfolio(Long userId) {
        List<Portfolio> portfolios = portfolioRepository.findByUserId(userId);
        return portfolios.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    // addToPortfolio, updatePortfolio, removeFromPortfolio 메서드는 
    // executeTrade() 제거로 인해 더 이상 사용되지 않습니다.
    // 교육생 실습을 위해 제거되었습니다.

    // Portfolio Get 특정 주식
    public PortfolioDto getUserStockPortfolio(Long userId, Long stockId) {
        Portfolio portfolio = portfolioRepository.findByUserIdAndStockIdWithQuery(userId, stockId) // 👈 Repository의 @Query 메서드 사용
                .orElseThrow(() -> new RuntimeException("해당 주식을 보유하고 있지 않습니다. userId: " + userId + ", stockId: " + stockId));

        return convertToDto(portfolio);
    }

    private PortfolioDto convertToDto(Portfolio portfolio) {
        Stock stock = portfolio.getStock();
        Long currentPrice = stock.getCurrentPrice() != null ? stock.getCurrentPrice() : 0L;
        Long quantity = portfolio.getQuantity() != null ? portfolio.getQuantity() : 0L;
        Long averagePrice = portfolio.getAveragePrice() != null ? portfolio.getAveragePrice() : 0L;

        Long totalValue = quantity * currentPrice;
        Long profitLoss = totalValue - (quantity * averagePrice);
        
        
        return PortfolioDto.builder()
                .id(portfolio.getId())
                .userId(portfolio.getUser().getId())
                .username(portfolio.getUser().getUsername())
                .stockId(stock.getId())
                .stockCode(stock.getCode())
                .stockName(stock.getName())
                .quantity(portfolio.getQuantity())
                .averagePrice(portfolio.getAveragePrice())
                .currentPrice(currentPrice)
                .totalValue(totalValue)
                .profitLoss(profitLoss)
                .build();
    }
}
