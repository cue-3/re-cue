package com.example.bookstore.service;

import com.example.bookstore.model.Book;
import com.example.bookstore.model.Order;
import com.example.bookstore.model.Order.OrderStatus;
import com.example.bookstore.model.OrderItem;
import com.example.bookstore.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * Service class for managing orders.
 * 
 * Provides business logic for order operations including creation,
 * status management, and order history.
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class OrderService {

    private final OrderRepository orderRepository;
    private final BookService bookService;

    /**
     * Get all orders
     */
    public List<Order> getAllOrders() {
        log.debug("Fetching all orders");
        return orderRepository.findAll();
    }

    /**
     * Get an order by ID
     */
    public Optional<Order> getOrderById(Long id) {
        log.debug("Fetching order with id: {}", id);
        return orderRepository.findById(id);
    }

    /**
     * Get orders by customer email
     */
    public List<Order> getOrdersByCustomer(String email) {
        log.debug("Fetching orders for customer: {}", email);
        return orderRepository.findByCustomerEmailIgnoreCase(email);
    }

    /**
     * Get orders by status
     */
    public List<Order> getOrdersByStatus(OrderStatus status) {
        log.debug("Fetching orders with status: {}", status);
        return orderRepository.findByStatus(status);
    }

    /**
     * Create a new order
     */
    @Transactional
    public Order createOrder(Order order) {
        log.info("Creating new order for customer: {}", order.getCustomerEmail());
        
        // Validate and set prices for each item
        for (OrderItem item : order.getItems()) {
            Book book = bookService.getBookById(item.getBook().getId())
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Book not found with id: " + item.getBook().getId()));
            
            // Check availability
            if (!bookService.isBookAvailable(book.getId(), item.getQuantity())) {
                throw new IllegalStateException(
                        "Book '" + book.getTitle() + "' is not available in requested quantity");
            }
            
            // Set current price
            item.setUnitPrice(book.getPrice());
            item.setBook(book);
        }
        
        // Calculate total
        order.calculateTotal();
        
        // Save order
        Order savedOrder = orderRepository.save(order);
        
        // Update book stock
        for (OrderItem item : savedOrder.getItems()) {
            Book book = item.getBook();
            bookService.updateStock(book.getId(), book.getStockQuantity() - item.getQuantity());
        }
        
        return savedOrder;
    }

    /**
     * Update order status
     */
    @Transactional
    public Order updateOrderStatus(Long id, OrderStatus newStatus) {
        log.info("Updating order {} status to {}", id, newStatus);
        
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Order not found with id: " + id));
        
        order.setStatus(newStatus);
        return orderRepository.save(order);
    }

    /**
     * Cancel an order
     */
    @Transactional
    public Order cancelOrder(Long id) {
        log.info("Cancelling order with id: {}", id);
        
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Order not found with id: " + id));
        
        if (order.getStatus() == OrderStatus.DELIVERED) {
            throw new IllegalStateException("Cannot cancel a delivered order");
        }
        
        if (order.getStatus() == OrderStatus.CANCELLED) {
            throw new IllegalStateException("Order is already cancelled");
        }
        
        // Restore book stock
        for (OrderItem item : order.getItems()) {
            Book book = item.getBook();
            bookService.updateStock(book.getId(), book.getStockQuantity() + item.getQuantity());
        }
        
        order.setStatus(OrderStatus.CANCELLED);
        return orderRepository.save(order);
    }

    /**
     * Get recent orders
     */
    public List<Order> getRecentOrders() {
        log.debug("Fetching recent orders");
        return orderRepository.findRecentOrders();
    }
}
