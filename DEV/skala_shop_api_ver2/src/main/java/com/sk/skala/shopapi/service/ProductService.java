package com.sk.skala.shopapi.service;

import com.sk.skala.shopapi.common.PagedList;
import com.sk.skala.shopapi.common.Response;
import com.sk.skala.shopapi.data.table.Product;
import com.sk.skala.shopapi.exception.Error;
import com.sk.skala.shopapi.exception.ParameterException;
import com.sk.skala.shopapi.exception.ResponseException;
import com.sk.skala.shopapi.repository.ProductRepository;
import com.sk.skala.shopapi.tools.StringUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    /**
     * 전체 상품 목록 조회 (페이지 단위 처리)
     */
    public Response getAllProducts(int offset, int count) {
        Pageable pageable = PageRequest.of(offset, count);
        Page<Product> page = productRepository.findAll(pageable);
        return new Response(new PagedList<>(page));
    }

    /**
     * 개별 상품 상세 조회
     */
    public Response getProductById(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));
        return new Response(product);
    }

    /**
     * 상품 등록
     * - 입력값 검증(productName, productPrice) 실패 시 ParameterException
     * - 상품명 중복 시 ResponseException(DATA_DUPLICATED)
     */
    public Response createProduct(Product product) {
        if (StringUtil.isEmpty(product.getProductName())
                || product.getProductPrice() == null || product.getProductPrice() <= 0) {
            throw new ParameterException("productName", "productPrice");
        }

        Optional<Product> existing = productRepository.findByProductName(product.getProductName());
        if (existing.isPresent()) {
            throw new ResponseException(Error.DATA_DUPLICATED, "이미 등록된 상품명입니다.");
        }

        // [버그 수정] id를 0L 등으로 강제 세팅하면 안 됨.
        // @GeneratedValue(strategy = IDENTITY) 전략에서 Hibernate는 id가 null일 때만
        // "신규 엔티티(INSERT 대상)"로 판단한다. id에 0이든 다른 값이든 채워서 저장하면
        // Hibernate가 이를 기존 엔티티로 오인해 UPDATE를 시도하다 실패(또는 잘못된 갱신)한다.
        // 따라서 신규 등록 시 id는 반드시 null 상태로 두어 JPA가 자동 생성하도록 한다.
        product.setId(null);
        Product saved = productRepository.save(product);
        return new Response(saved);
    }

    /**
     * 상품 정보 수정
     */
    public Response updateProduct(Product product) {
        if (StringUtil.isEmpty(product.getProductName())
                || product.getProductPrice() == null || product.getProductPrice() <= 0) {
            throw new ParameterException("productName", "productPrice");
        }

        Product existing = productRepository.findById(product.getId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        existing.setProductName(product.getProductName());
        existing.setProductPrice(product.getProductPrice());

        Product saved = productRepository.save(existing);
        return new Response(saved);
    }

    /**
     * 상품 삭제
     */
    public Response deleteProduct(Product product) {
        Product existing = productRepository.findById(product.getId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        productRepository.delete(existing);
        return new Response("상품이 삭제되었습니다.");
    }
}
