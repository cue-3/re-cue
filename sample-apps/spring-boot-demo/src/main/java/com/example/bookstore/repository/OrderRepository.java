package com.example.bookstore.repository;

import com.example.bookstore.model.Order;
import com.example.bookstore.model.Order.OrderStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository interface for Order entity.
 * 
 * Provides data access methods for orders including filtering by status and customer.
 */
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    /**
     * Find orders by customer email
     */
    List<Order> findByCustomerEmailIgnoreCase(String email);

    /**
     * Find orders by status
     */
    List<Order> findByStatus(OrderStatus status);

    /**
     * Find orders within a date range
     */
    List<Order> findByOrderDateBetween(LocalDateTime startDate, LocalDateTime endDate);

    /**
     * Find recent orders
     */
    @Query("SELECT o FROM Order o ORDER BY o.orderDate DESC")
    List<Order> findRecentOrders();

    /**
     * Find orders by customer email and status
     */
    List<Order> findByCustomerEmailIgnoreCaseAndStatus(String email, OrderStatus status);
}
