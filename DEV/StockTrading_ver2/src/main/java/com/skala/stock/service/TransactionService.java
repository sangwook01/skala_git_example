package com.skala.stock.service;

import com.skala.stock.dto.TradeRequestDto;
import com.skala.stock.dto.TransactionDto;
import com.skala.stock.entity.Transaction;
import com.skala.stock.repository.StockRepository;
import com.skala.stock.repository.TransactionRepository;
import com.skala.stock.repository.UserRepository;
import com.skala.stock.repository.PortfolioRepository;
import com.skala.stock.entity.*;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final UserRepository userRepository;        
    private final StockRepository stockRepository;  
    private final PortfolioRepository portfolioRepository;
    
    @Transactional(readOnly = true, propagation = Propagation.SUPPORTS)
    public List<TransactionDto> getUserTransactions(Long userId) {
        List<Transaction> transactions = transactionRepository.findByUserIdOrderByTransactionDateDesc(userId);
        return transactions.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    // Transaction GET by ID (거래 상세 조회)
    public TransactionDto getTransactionById(Long id) {
        // Repository에서 만든 @Query 메서드 호출
        Transaction transaction = transactionRepository.findByIdWithQuery(id)
                .orElseThrow(() -> new RuntimeException("거래 내역을 찾을 수 없습니다. ID: " + id));
        return convertToDto(transaction);
    }

    // Transaction POST /trade (주식 매매 실행)
    @Transactional
    public TransactionDto executeTrade(TradeRequestDto tradeRequest) {
        User user = userRepository.findById(tradeRequest.getUserId())
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다: " + tradeRequest.getUserId()));

        Stock stock = stockRepository.findById(tradeRequest.getStockId())
                .orElseThrow(() -> new RuntimeException("주식을 찾을 수 없습니다. ID: " + tradeRequest.getStockId()));

        Long currentPrice = stock.getCurrentPrice();
        Long totalAmount = currentPrice * tradeRequest.getQuantity();

        // 매수(BUY) / 매도(SELL) 로직
        if (tradeRequest.getType() == Transaction.TransactionType.BUY) {
            if (user.getBalance() < totalAmount) {
                throw new RuntimeException("잔액이 부족합니다. 현재 잔액: " + user.getBalance());
            }
            user.setBalance(user.getBalance() - totalAmount);
            
            Portfolio portfolio = portfolioRepository.findByUserIdAndStockId(user.getId(), stock.getId())
                    .orElse(null);

            if (portfolio == null) {
                // 최초 매수: 현재 주가가 평단가가 됨
                portfolio = Portfolio.builder()
                        .user(user)
                        .stock(stock)
                        .quantity(tradeRequest.getQuantity())
                        .averagePrice(currentPrice)
                        .build();
            } else {
                // 추가 매수: (기존 총매수액 + 이번 총매수액) / 전체 수량으로 평단가 재계산
                Long oldQuantity = portfolio.getQuantity();
                Long oldAvgPrice = portfolio.getAveragePrice() != null ? portfolio.getAveragePrice() : currentPrice;
                Long newQuantity = oldQuantity + tradeRequest.getQuantity();

                Long newAvgPrice = ((oldQuantity * oldAvgPrice) + totalAmount) / newQuantity;

                portfolio.setQuantity(newQuantity);
                portfolio.setAveragePrice(newAvgPrice);
            }

            portfolioRepository.save(portfolio);

        } else if (tradeRequest.getType() == Transaction.TransactionType.SELL) {
            Portfolio portfolio = portfolioRepository.findByUserIdAndStockId(user.getId(), stock.getId())
                    .orElseThrow(() -> new RuntimeException("보유하지 않은 주식입니다: " + stock.getName()));

            if (portfolio.getQuantity() < tradeRequest.getQuantity()) {
                throw new RuntimeException("보유 수량이 부족합니다. 현재 수량: " + portfolio.getQuantity());
            }

            portfolio.setQuantity(portfolio.getQuantity() - tradeRequest.getQuantity());
            user.setBalance(user.getBalance() + totalAmount);
            
            if (portfolio.getQuantity() == 0) {
                portfolioRepository.delete(portfolio);
            }
        }

        // 거래 내역 생성 및 저장
        Transaction transaction = Transaction.builder()
                .user(user)
                .stock(stock)
                .type(tradeRequest.getType())
                .quantity(tradeRequest.getQuantity())
                .price(currentPrice)
                .totalAmount(totalAmount)
                .build();

        Transaction savedTransaction = transactionRepository.save(transaction);
        return convertToDto(savedTransaction);
    }

    private TransactionDto convertToDto(Transaction transaction) {
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