package com.skala.stock.service;

import com.skala.stock.dto.StockDto;
import com.skala.stock.entity.Stock;
import com.skala.stock.repository.StockRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class StockService {

    private final StockRepository stockRepository;

    @Transactional
    public StockDto createStock(StockDto stockDto) {
        if (stockRepository.existsByCode(stockDto.getCode())) {
            throw new RuntimeException("이미 존재하는 종목 코드입니다: " + stockDto.getCode());
        }

        Stock stock = Stock.builder()
                .code(stockDto.getCode())
                .name(stockDto.getName())
                .currentPrice(stockDto.getCurrentPrice())
                .previousPrice(stockDto.getPreviousPrice())
                .build();

        Stock savedStock = stockRepository.save(stock);
        return convertToDto(savedStock);
    }

    public StockDto getStockById(Long id) {
        Stock stock = stockRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("주식을 찾을 수 없습니다: " + id));
        return convertToDto(stock);
    }

    public List<StockDto> getAllStocks() {
        return stockRepository.findAll().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

// 주식 정보 수정
    @Transactional
    public StockDto updateStock(Long id, StockDto stockDto) {
        Stock stock = stockRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("주식을 찾을 수 없습니다: " + id));

        // 종목 코드를 변경하려고 하고, 그 코드가 기존 본인 코드가 아니라면 중복 검사
        if (stockDto.getCode() != null && !stockDto.getCode().equals(stock.getCode())) {
            if (stockRepository.existsByCode(stockDto.getCode())) {
                throw new RuntimeException("이미 존재하는 종목 코드입니다: " + stockDto.getCode());
            }
            stock.setCode(stockDto.getCode());
        }

        if (stockDto.getName() != null) {
            stock.setName(stockDto.getName());
        }
        if (stockDto.getCurrentPrice() != null) {
            stock.setCurrentPrice(stockDto.getCurrentPrice());
        }
        if (stockDto.getPreviousPrice() != null) {
            stock.setPreviousPrice(stockDto.getPreviousPrice());
        }

        return convertToDto(stock);
    }

    // 주식 정보 삭제
    @Transactional
    public void deleteStock(Long id) {
        if (!stockRepository.existsById(id)) {
            throw new RuntimeException("주식을 찾을 수 없습니다: " + id);
        }
        // deleteById와 같은 경우는 따로 method를 만들지 않아도 JpaRepository에서 제공하는 기본 메서드를 사용하면 됩니다.
        stockRepository.deleteById(id);
    }

    // 종목 코드로 조회
    public StockDto getStockByCode(String code) {
        Stock stock = stockRepository.findByCode(code)
                .orElseThrow(() -> new RuntimeException("해당 종목 코드의 주식을 찾을 수 없습니다: " + code));
        return convertToDto(stock);
    }

    private StockDto convertToDto(Stock stock) {
        return StockDto.builder()
                .id(stock.getId())
                .code(stock.getCode())
                .name(stock.getName())
                .currentPrice(stock.getCurrentPrice())
                .previousPrice(stock.getPreviousPrice())
                .build();
    }
}
