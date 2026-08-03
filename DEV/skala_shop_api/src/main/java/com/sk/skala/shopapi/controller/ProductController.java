package com.sk.skala.shopapi.controller;

import com.sk.skala.shopapi.common.Response;
import com.sk.skala.shopapi.data.table.Product;
import com.sk.skala.shopapi.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    /**
     * 상품 전체 목록 조회 (페이지 단위 처리)
     * - API 목록 표(GET /api/products)와 실습 4-1 예시 코드(GET /api/products/list)가
     *   서로 다른 경로를 제시하고 있어, 두 경로 모두 지원하도록 처리함
     */
    @GetMapping({"", "/list"})
    public Response getAllProducts(@RequestParam(defaultValue = "0") Integer offset,
                                    @RequestParam(defaultValue = "10") Integer count) {
        return productService.getAllProducts(offset, count);
    }

    /** ID에 해당하는 개별 상품 상세 정보 */
    @GetMapping("/{id}")
    public Response getProductById(@PathVariable Long id) {
        return productService.getProductById(id);
    }

    /** 상품 정보 추가 */
    @PostMapping
    public Response createProduct(@RequestBody Product product) {
        return productService.createProduct(product);
    }

    /** 상품 정보 변경 */
    @PutMapping
    public Response updateProduct(@RequestBody Product product) {
        return productService.updateProduct(product);
    }

    /** 상품 정보 삭제 */
    @DeleteMapping
    public Response deleteProduct(@RequestBody Product product) {
        return productService.deleteProduct(product);
    }
}
