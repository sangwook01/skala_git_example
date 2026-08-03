package com.sk.skala.shopapi.controller;

import com.sk.skala.shopapi.common.Response;
import com.sk.skala.shopapi.data.dto.CustomerSession;
import com.sk.skala.shopapi.data.dto.OrderRequest;
import com.sk.skala.shopapi.data.table.Customer;
import com.sk.skala.shopapi.service.CustomerService;
import jakarta.servlet.http.HttpServletResponse;
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
@RequestMapping("/api/customers")
@RequiredArgsConstructor
public class CustomerController {

    private final CustomerService customerService;

    /** 고객 전체 목록 조회 (페이지 단위 처리) */
    @GetMapping
    public Response getAllCustomers(@RequestParam(value = "offset", defaultValue = "0") int offset,
                                     @RequestParam(value = "count", defaultValue = "10") int count) {
        return customerService.getAllCustomers(offset, count);
    }

    /**
     * ID 또는 Name에 해당하는 고객 상세 정보 + 주문 상품 목록
     * - API 목록 표의 GET /api/customers/{customerId} 와 GET /api/customers/{customerName}
     *   두 행을 하나의 엔드포인트로 지원 (customerId로 먼저 찾고, 없으면 customerName으로 조회)
     */
    @GetMapping("/{customerId}")
    public Response getCustomerByIdOrName(@PathVariable String customerId) {
        return customerService.getCustomerByIdOrName(customerId);
    }

    /** 고객 정보 추가 (회원가입) */
    @PostMapping
    public Response createCustomer(@RequestBody Customer customer) {
        return customerService.createCustomer(customer);
    }

    /** 고객 로그인 -> JWT 발급(Set-Cookie: bff-access) */
    @PostMapping("/login")
    public Response loginCustomer(@RequestBody CustomerSession customerSession,
                                   HttpServletResponse httpResponse) {
        return customerService.loginCustomer(customerSession, httpResponse);
    }

    /** 고객 정보 변경 */
    @PutMapping
    public Response updateCustomer(@RequestBody Customer customer) {
        return customerService.updateCustomer(customer);
    }

    /** 고객 정보 삭제 */
    @DeleteMapping("/{customerId}")
    public Response deleteCustomer(@PathVariable String customerId) {
        Customer customer = new Customer();
        customer.setCustomerId(customerId);
        return customerService.deleteCustomer(customer);
    }

    /** 고객이 보유(주문)한 상품 정보만 조회 */
    @GetMapping("/{customerId}/products")
    public Response getCustomerProducts(@PathVariable String customerId) {
        return customerService.getCustomerById(customerId);
    }

    /** 고객의 상품 주문 (JWT 필요, 포인트 차감) */
    @PostMapping("/order")
    public Response placeOrder(@RequestBody OrderRequest order) {
        return customerService.placeOrder(order);
    }

    /** 고객의 주문 취소 (JWT 필요, 포인트 환급) */
    @PostMapping("/cancel")
    public Response cancelOrder(@RequestBody OrderRequest order) {
        return customerService.cancelOrder(order);
    }
}
