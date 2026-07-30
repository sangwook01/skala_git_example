package com.skala.stock.controller;

// StockAnalysisController는 모든 기능이 제거되었습니다.
// 교육생 실습을 위해 이 컨트롤러는 삭제되었습니다.

import com.skala.stock.dto.TransactionDto;
import com.skala.stock.service.StockAnalysisService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
@Tag(name = "주식/자산 분석 API", description = "포트폴리오 평가 손익, 자산 및 거래 내역 분석 API")
public class StockAnalysisController {

    private final StockAnalysisService stockAnalysisService;

    // 1. Analysis 포트폴리오 평가 손익 조회
    @GetMapping("/user/{userId}/profit-loss")
    @Operation(summary = "포트폴리오 평가 손익 조회", description = "사용자의 보유 주식 전체 평가 손익금액을 조회합니다.")
    public ResponseEntity<Long> getPortfolioProfitLoss(@PathVariable Long userId) {
        Long profitLoss = stockAnalysisService.getPortfolioProfitLoss(userId);
        return ResponseEntity.ok(profitLoss);
    }

    // 2. Analysis 거래 내역 상세 조회
    @GetMapping("/transaction/{transactionId}")
    @Operation(summary = "거래 내역 상세 조회", description = "거래 ID로 특정 거래 내역의 상세 정보를 조회합니다.")
    public ResponseEntity<TransactionDto> getTransactionDetail(@PathVariable Long transactionId) {
        TransactionDto transactionDto = stockAnalysisService.getTransactionDetail(transactionId);
        return ResponseEntity.ok(transactionDto);
    }

    // 3. Analysis 특정 주식 거래 내역 조회
    @GetMapping("/user/{userId}/stock/{stockId}/transactions")
    @Operation(summary = "특정 주식 거래 내역 조회", description = "특정 사용자의 특정 주식에 대한 전체 매매 내역을 조회합니다.")
    public ResponseEntity<List<TransactionDto>> getUserStockTransactions(
            @PathVariable Long userId,
            @PathVariable Long stockId) {
        List<TransactionDto> transactions = stockAnalysisService.getUserStockTransactions(userId, stockId);
        return ResponseEntity.ok(transactions);
    }

    // 4. Analysis 총 자산 조회
    @GetMapping("/user/{userId}/total-assets")
    @Operation(summary = "총 자산 조회", description = "사용자의 예수금과 주식 평가액을 합산한 총 자산을 조회합니다.")
    public ResponseEntity<Long> getTotalAssets(@PathVariable Long userId) {
        Long totalAssets = stockAnalysisService.getTotalAssets(userId);
        return ResponseEntity.ok(totalAssets);
    }

    // 5. Analysis 총 수익률 조회
    @GetMapping("/user/{userId}/total-return-rate")
    @Operation(summary = "총 수익률 조회", description = "사용자의 보유 주식 전체 평가 수익률(%)을 조회합니다.")
    public ResponseEntity<Double> getTotalReturnRate(@PathVariable Long userId) {
        Double totalReturnRate = stockAnalysisService.getTotalReturnRate(userId);
        return ResponseEntity.ok(totalReturnRate);
    }
}