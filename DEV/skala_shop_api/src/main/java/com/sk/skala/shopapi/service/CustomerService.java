package com.sk.skala.shopapi.service;

import com.sk.skala.shopapi.common.PagedList;
import com.sk.skala.shopapi.common.Response;
import com.sk.skala.shopapi.common.SessionHandler;
import com.sk.skala.shopapi.data.dto.CustomerSession;
import com.sk.skala.shopapi.data.dto.OrderItemDto;
import com.sk.skala.shopapi.data.dto.OrderListDto;
import com.sk.skala.shopapi.data.dto.OrderRequest;
import com.sk.skala.shopapi.data.table.Customer;
import com.sk.skala.shopapi.data.table.OrderItem;
import com.sk.skala.shopapi.data.table.Product;
import com.sk.skala.shopapi.exception.Error;
import com.sk.skala.shopapi.exception.ParameterException;
import com.sk.skala.shopapi.exception.ResponseException;
import com.sk.skala.shopapi.repository.CustomerRepository;
import com.sk.skala.shopapi.repository.OrderItemRepository;
import com.sk.skala.shopapi.repository.ProductRepository;
import com.sk.skala.shopapi.tools.StringUtil;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CustomerService {

    /** 회원가입 시 지급되는 초기 포인트 */
    private static final double INITIAL_POINT = 1_000_000.0;

    private final ProductRepository productRepository;
    private final CustomerRepository customerRepository;
    private final OrderItemRepository orderItemRepository;
    private final SessionHandler sessionHandler;

    /**
     * 전체 고객 목록 조회 (페이지 단위 처리)
     */
    public Response getAllCustomers(int offset, int count) {
        Pageable pageable = PageRequest.of(offset, count);
        Page<Customer> page = customerRepository.findAll(pageable);
        // [버그 수정] 목록 조회 응답에 비밀번호가 그대로 노출되고 있었음 -> null 처리
        page.getContent().forEach(c -> c.setCustomerPassword(null));
        return new Response(new PagedList<>(page));
    }

    /**
     * 단일 고객 및 보유(주문) 상품 목록 조회
     */
    @Transactional(readOnly = true)
    public Response getCustomerById(String customerId) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Customer not found"));

        List<OrderItem> orderItems = orderItemRepository.findItemsWithProductByCustomerId(customerId);

        List<OrderItemDto> productDtos = orderItems.stream()
                .map(item -> OrderItemDto.builder()
                        .productId(item.getProduct().getId())
                        .productName(item.getProduct().getProductName())
                        .productPrice(item.getProduct().getProductPrice())
                        .quantity(item.getQuantity())
                        .build())
                .collect(Collectors.toList());

        OrderListDto dto = OrderListDto.builder()
                .customerId(customer.getCustomerId())
                .customerPoint(customer.getCustomerPoint())
                .products(productDtos)
                .build();

        return new Response(dto);
    }

    /**
     * 고객 생성 (회원가입) - 초기 포인트 지급
     */
    public Response createCustomer(Customer customer) {
        if (StringUtil.isAnyEmpty(customer.getCustomerId(), customer.getCustomerPassword())) {
            throw new ParameterException("customerId", "customerPassword");
        }

        if (customerRepository.existsById(customer.getCustomerId())) {
            throw new ResponseException(Error.DATA_DUPLICATED, "이미 존재하는 고객 ID입니다.");
        }

        // [버그 수정] 클라이언트가 요청 본문에 customerPoint를 실어 보내면
        // 그 값이 그대로 초기 포인트가 되어버리는 문제가 있었음(임의 포인트 조작 가능).
        // 회원가입 시 초기 포인트는 항상 서버가 정한 고정값으로만 지급한다.
        customer.setCustomerPoint(INITIAL_POINT);

        Customer saved = customerRepository.save(customer);
        saved.setCustomerPassword(null); // 응답에는 비밀번호 노출하지 않음
        return new Response(saved);
    }

    /**
     * 고객 로그인 - 성공 시 JWT를 Cookie(bff-access)로 발급
     */
    public Response loginCustomer(CustomerSession customerSession, HttpServletResponse httpResponse) {
        if (StringUtil.isAnyEmpty(customerSession.getCustomerId(), customerSession.getCustomerPassword())) {
            throw new ParameterException("customerId", "customerPassword");
        }

        Customer customer = customerRepository.findById(customerSession.getCustomerId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));

        if (!customer.getCustomerPassword().equals(customerSession.getCustomerPassword())) {
            throw new ResponseException(Error.NOT_AUTHENTICATED, "비밀번호가 일치하지 않습니다.");
        }

        sessionHandler.storeAccessToken(customer.getCustomerId(), httpResponse);

        customer.setCustomerPassword(null);
        return new Response(customer);
    }

    /**
     * 고객 정보(포인트 등) 업데이트
     */
    public Response updateCustomer(Customer customer) {
        if (StringUtil.isEmpty(customer.getCustomerId()) || customer.getCustomerPoint() == null) {
            throw new ResponseException(Error.DATA_NOT_FOUND, "고객 정보가 올바르지 않습니다.");
        }

        Customer existing = customerRepository.findById(customer.getCustomerId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));

        existing.setCustomerPoint(customer.getCustomerPoint());
        Customer saved = customerRepository.save(existing);
        saved.setCustomerPassword(null);
        return new Response(saved);
    }

    /**
     * 고객 삭제
     */
    public Response deleteCustomer(Customer customer) {
        Customer existing = customerRepository.findById(customer.getCustomerId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));

        customerRepository.delete(existing);
        return new Response("고객이 삭제되었습니다.");
    }

    /**
     * 상품 주문 - 로그인(JWT) 필수, 포인트 차감, 재주문 시 수량 누적
     */
    @Transactional
    public Response placeOrder(OrderRequest order) {
        // [버그 수정] 수량 검증 누락 - quantity가 없거나 0 이하(음수 포함)여도
        // 그대로 진행되어, 음수 수량 주문 시 포인트 부족 검사(< totalPrice)를 우회하고
        // 오히려 포인트가 증가하는 취약점이 있었음.
        if (order.getProductId() == null || order.getQuantity() == null || order.getQuantity() <= 0) {
            throw new ParameterException("productId", "quantity");
        }

        String customerId = sessionHandler.getCurrentCustomerId();

        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));

        Product product = productRepository.findById(order.getProductId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        double totalPrice = product.getProductPrice() * order.getQuantity();

        if (customer.getCustomerPoint() < totalPrice) {
            throw new ResponseException(Error.INSUFFICIENT_FUNDS, "포인트가 부족합니다.");
        }

        // 포인트 차감
        customer.setCustomerPoint(customer.getCustomerPoint() - totalPrice);

        // 같은 상품 재주문 시 수량 누적, 없으면 신규 생성
        Optional<OrderItem> existingItem = orderItemRepository.findByCustomerAndProduct(customer, product);
        if (existingItem.isPresent()) {
            OrderItem item = existingItem.get();
            item.setQuantity(item.getQuantity() + order.getQuantity());
            orderItemRepository.save(item);
        } else {
            orderItemRepository.save(new OrderItem(customer, product, order.getQuantity()));
        }

        customerRepository.save(customer);

        return new Response("주문이 완료되었습니다. 남은 포인트: " + customer.getCustomerPoint());
    }

    /**
     * 주문 취소 - 로그인(JWT) 필수, 수량 차감(0이면 삭제), 포인트 환급
     */
    @Transactional
    public Response cancelOrder(OrderRequest order) {
        // [버그 수정] 주문과 동일하게 취소 요청도 수량 검증이 없었음
        if (order.getProductId() == null || order.getQuantity() == null || order.getQuantity() <= 0) {
            throw new ParameterException("productId", "quantity");
        }

        String customerId = sessionHandler.getCurrentCustomerId();

        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "고객을 찾을 수 없습니다."));

        Product product = productRepository.findById(order.getProductId())
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "상품을 찾을 수 없습니다."));

        OrderItem item = orderItemRepository.findByCustomerAndProduct(customer, product)
                .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "주문 내역을 찾을 수 없습니다."));

        if (item.getQuantity() < order.getQuantity()) {
            throw new ResponseException(Error.INSUFFICIENT_QUANTITY, "취소할 수량이 주문 수량보다 많습니다.");
        }

        int remaining = item.getQuantity() - order.getQuantity();
        double refund = product.getProductPrice() * order.getQuantity();

        if (remaining == 0) {
            orderItemRepository.delete(item);
        } else {
            item.setQuantity(remaining);
            orderItemRepository.save(item);
        }

        // 포인트 환급
        customer.setCustomerPoint(customer.getCustomerPoint() + refund);
        customerRepository.save(customer);

        return new Response("주문이 취소되었습니다. 남은 포인트: " + customer.getCustomerPoint());
    }
}
