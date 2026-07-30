package com.skala.stock.service;

// StockAnalysisService는 모든 기능이 제거되었습니다.
// 교육생 실습을 위해 이 서비스는 삭제되었습니다.
import com.skala.stock.dto.TransactionDto;
import com.skala.stock.entity.Portfolio;
import com.skala.stock.entity.Transaction;
import com.skala.stock.entity.User;
import com.skala.stock.repository.PortfolioRepository;
import com.skala.stock.repository.TransactionRepository;
import com.skala.stock.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class StockAnalysisService {

    private final UserRepository userRepository;
    private final PortfolioRepository portfolioRepository;
    private final TransactionRepository transactionRepository;

    // 1. Analysis 포트폴리오 평가 손익 조회
    public Long getPortfolioProfitLoss(Long userId) {
        List<Portfolio> portfolios = portfolioRepository.findByUserId(userId);
        
        long totalValue = 0L;
        long totalCost = 0L;

        for (Portfolio p : portfolios) {
            long currentPrice = p.getStock().getCurrentPrice() != null ? p.getStock().getCurrentPrice() : 0L;
            long quantity = p.getQuantity() != null ? p.getQuantity() : 0L;
            long averagePrice = p.getAveragePrice() != null ? p.getAveragePrice() : 0L;

            totalValue += currentPrice * quantity;
            totalCost += averagePrice * quantity;
        }

        return totalValue - totalCost; // 총 평가 손익 (원)
    }

    // 2. Analysis 거래 내역 상세 조회
    public TransactionDto getTransactionDetail(Long transactionId) {
        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new RuntimeException("거래 내역을 찾을 수 없습니다. ID: " + transactionId));

        return convertToTransactionDto(transaction);
    }

    // 3. Analysis 특정 주식 거래 내역 조회
    public List<TransactionDto> getUserStockTransactions(Long userId, Long stockId) {
        // 특정 사용자의 특정 주식 거래 내역 조회
        List<Transaction> transactions = transactionRepository.findByUserIdOrderByTransactionDateDesc(userId)
                .stream()
                .filter(t -> t.getStock().getId().equals(stockId))
                .collect(Collectors.toList());

        return transactions.stream()
                .map(this::convertToTransactionDto)
                .collect(Collectors.toList());
    }

    // 4. Analysis 총 자산 조회 (예수금 + 포트폴리오 평가 금액)
    public Long getTotalAssets(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다. ID: " + userId));

        long balance = user.getBalance() != null ? user.getBalance() : 0L;

        List<Portfolio> portfolios = portfolioRepository.findByUserId(userId);
        long stockTotalValue = portfolios.stream()
                .mapToLong(p -> {
                    long currentPrice = p.getStock().getCurrentPrice() != null ? p.getStock().getCurrentPrice() : 0L;
                    long quantity = p.getQuantity() != null ? p.getQuantity() : 0L;
                    return currentPrice * quantity;
                })
                .sum();

        return balance + stockTotalValue; // 총 자산 = 예수금 + 주식 평가액
    }

    // 5. Analysis 총 수익률 조회 (%)
    public Double getTotalReturnRate(Long userId) {
        List<Portfolio> portfolios = portfolioRepository.findByUserId(userId);

        long totalValue = 0L;
        long totalCost = 0L;

        for (Portfolio p : portfolios) {
            long currentPrice = p.getStock().getCurrentPrice() != null ? p.getStock().getCurrentPrice() : 0L;
            long quantity = p.getQuantity() != null ? p.getQuantity() : 0L;
            long averagePrice = p.getAveragePrice() != null ? p.getAveragePrice() : 0L;

            totalValue += currentPrice * quantity;
            totalCost += averagePrice * quantity;
        }

        if (totalCost == 0L) {
            return 0.0; // 매수 금액이 없으면 수익률 0.0%
        }

        // 수익률 = ((평가금액 - 매수금액) / 매수금액) * 100
        double profitLoss = (double) (totalValue - totalCost);
        return (profitLoss / totalCost) * 100.0;
    }

    // Transaction DTO 변환 헬퍼 메서드
    private TransactionDto convertToTransactionDto(Transaction transaction) {
        return TransactionDto.builder()
                .id(transaction.getId())
                .userId(transaction.getUser().getId())
                .username(transaction.getUser().getUsername())
                .stockId(transaction.getStock().getId())
                .stockCode(transaction.getStock().getCode())
                .stockName(transaction.getStock().getName())
                .type(transaction.getType())
                .quantity(transaction.getQuantity())
                .price(transaction.getPrice())
                .totalAmount(transaction.getTotalAmount())
                .transactionDate(transaction.getTransactionDate())
                .createdAt(transaction.getCreatedAt())
                .build();
    }
}