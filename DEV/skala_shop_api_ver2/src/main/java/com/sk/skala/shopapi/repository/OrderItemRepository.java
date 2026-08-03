package com.sk.skala.shopapi.repository;

import com.sk.skala.shopapi.data.table.Customer;
import com.sk.skala.shopapi.data.table.OrderItem;
import com.sk.skala.shopapi.data.table.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {

    /**
     * 속성 순회(Property Traversal) 활용:
     * OrderItem.customer가 참조하는 Customer 엔티티의 customerId 필드 값으로 조회
     * (아래 두 메서드는 동일하게 동작함 - JPA 쿼리 메소드 작명 가이드 참고)
     *   List<OrderItem> findByCustomer_CustomerId(String customerId)
     *   List<OrderItem> findItemsByCustomer(Customer customer)
     */
    List<OrderItem> findByCustomer_CustomerId(String customerId);

    /**
     * 고객 객체를 직접 전달받는 방식의 속성 순회 조회
     */
    List<OrderItem> findByCustomer(Customer customer);

    /**
     * 특정 고객이 특정 상품을 이미 주문(보유)하고 있는지 조회
     * - 주문 시: 존재하면 수량 누적, 없으면 신규 생성
     * - 취소 시: 존재하는 항목의 수량을 차감
     */
    Optional<OrderItem> findByCustomerAndProduct(Customer customer, Product product);

    /**
     * @Query(JPQL)를 이용한 복잡한 조회 예시
     * - N+1 문제를 피하기 위해 fetch join으로 Product를 함께 조회
     * - 주문 순서(id) 기준으로 정렬하여 반환
     */
    @Query("select oi from OrderItem oi " +
           "join fetch oi.product " +
           "where oi.customer.customerId = :customerId " +
           "order by oi.id asc")
    List<OrderItem> findItemsWithProductByCustomerId(@Param("customerId") String customerId);
}
