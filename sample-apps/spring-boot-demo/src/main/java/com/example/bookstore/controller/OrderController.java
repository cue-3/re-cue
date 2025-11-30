package com.example.bookstore.controller;

import com.example.bookstore.model.Order;
import com.example.bookstore.model.Order.OrderStatus;
import com.example.bookstore.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for order management operations.
 * 
 * Provides endpoints for creating orders, updating order status,
 * and retrieving order history.
 */
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    /**
     * Get all orders
     * 
     * @return List of all orders
     */
    @GetMapping
    public ResponseEntity<List<Order>> getAllOrders() {
        List<Order> orders = orderService.getAllOrders();
        return ResponseEntity.ok(orders);
    }

    /**
     * Get an order by ID
     * 
     * @param id Order ID
     * @return Order details
     */
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrderById(@PathVariable Long id) {
        return orderService.getOrderById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get orders by customer email
     * 
     * @param email Customer email address
     * @return List of customer orders
     */
    @GetMapping("/customer")
    public ResponseEntity<List<Order>> getOrdersByCustomer(@RequestParam String email) {
        List<Order> orders = orderService.getOrdersByCustomer(email);
        return ResponseEntity.ok(orders);
    }

    /**
     * Get orders by status
     * 
     * @param status Order status
     * @return List of orders with the specified status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<Order>> getOrdersByStatus(@PathVariable OrderStatus status) {
        List<Order> orders = orderService.getOrdersByStatus(status);
        return ResponseEntity.ok(orders);
    }

    /**
     * Get recent orders
     * 
     * @return List of recent orders
     */
    @GetMapping("/recent")
    public ResponseEntity<List<Order>> getRecentOrders() {
        List<Order> orders = orderService.getRecentOrders();
        return ResponseEntity.ok(orders);
    }

    /**
     * Create a new order
     * 
     * @param order Order details
     * @return Created order
     */
    @PostMapping
    public ResponseEntity<?> createOrder(@Valid @RequestBody Order order) {
        try {
            Order createdOrder = orderService.createOrder(order);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdOrder);
        } catch (IllegalArgumentException | IllegalStateException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    /**
     * Update order status
     * 
     * @param id Order ID
     * @param status New status
     * @return Updated order
     */
    @PatchMapping("/{id}/status")
    public ResponseEntity<?> updateOrderStatus(
            @PathVariable Long id,
            @RequestParam OrderStatus status) {
        try {
            Order updatedOrder = orderService.updateOrderStatus(id, status);
            return ResponseEntity.ok(updatedOrder);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Cancel an order
     * 
     * @param id Order ID
     * @return Cancelled order
     */
    @PostMapping("/{id}/cancel")
    public ResponseEntity<?> cancelOrder(@PathVariable Long id) {
        try {
            Order cancelledOrder = orderService.cancelOrder(id);
            return ResponseEntity.ok(cancelledOrder);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        } catch (IllegalStateException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}
