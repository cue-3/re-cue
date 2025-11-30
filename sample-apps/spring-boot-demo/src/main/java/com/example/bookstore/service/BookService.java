package com.example.bookstore.service;

import com.example.bookstore.model.Book;
import com.example.bookstore.model.Book.BookStatus;
import com.example.bookstore.repository.BookRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * Service class for managing books.
 * 
 * Provides business logic for book operations including CRUD operations,
 * search functionality, and inventory management.
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class BookService {

    private final BookRepository bookRepository;

    /**
     * Get all books
     */
    public List<Book> getAllBooks() {
        log.debug("Fetching all books");
        return bookRepository.findAll();
    }

    /**
     * Get a book by ID
     */
    public Optional<Book> getBookById(Long id) {
        log.debug("Fetching book with id: {}", id);
        return bookRepository.findById(id);
    }

    /**
     * Get a book by ISBN
     */
    public Optional<Book> getBookByIsbn(String isbn) {
        log.debug("Fetching book with ISBN: {}", isbn);
        return bookRepository.findByIsbn(isbn);
    }

    /**
     * Search books by title or author
     */
    public List<Book> searchBooks(String searchTerm) {
        log.debug("Searching books with term: {}", searchTerm);
        return bookRepository.searchBooks(searchTerm);
    }

    /**
     * Get available books
     */
    public List<Book> getAvailableBooks() {
        log.debug("Fetching available books");
        return bookRepository.findAvailableBooks();
    }

    /**
     * Create a new book
     */
    @Transactional
    public Book createBook(Book book) {
        log.info("Creating new book: {}", book.getTitle());
        
        if (bookRepository.existsByIsbn(book.getIsbn())) {
            throw new IllegalArgumentException("Book with ISBN " + book.getIsbn() + " already exists");
        }
        
        return bookRepository.save(book);
    }

    /**
     * Update an existing book
     */
    @Transactional
    public Book updateBook(Long id, Book bookDetails) {
        log.info("Updating book with id: {}", id);
        
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Book not found with id: " + id));

        book.setTitle(bookDetails.getTitle());
        book.setAuthor(bookDetails.getAuthor());
        book.setPrice(bookDetails.getPrice());
        book.setDescription(bookDetails.getDescription());
        book.setStockQuantity(bookDetails.getStockQuantity());
        book.setStatus(bookDetails.getStatus());
        book.setPublishedYear(bookDetails.getPublishedYear());

        return bookRepository.save(book);
    }

    /**
     * Update book stock quantity
     */
    @Transactional
    public Book updateStock(Long id, Integer quantity) {
        log.info("Updating stock for book id: {} to quantity: {}", id, quantity);
        
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Book not found with id: " + id));

        book.setStockQuantity(quantity);
        
        // Update status based on stock
        if (quantity == 0) {
            book.setStatus(BookStatus.OUT_OF_STOCK);
        } else if (book.getStatus() == BookStatus.OUT_OF_STOCK) {
            book.setStatus(BookStatus.AVAILABLE);
        }

        return bookRepository.save(book);
    }

    /**
     * Delete a book
     */
    @Transactional
    public void deleteBook(Long id) {
        log.info("Deleting book with id: {}", id);
        
        if (!bookRepository.existsById(id)) {
            throw new IllegalArgumentException("Book not found with id: " + id);
        }
        
        bookRepository.deleteById(id);
    }

    /**
     * Check if book is available for purchase
     */
    public boolean isBookAvailable(Long id, Integer quantity) {
        Optional<Book> book = bookRepository.findById(id);
        return book.isPresent() 
                && book.get().getStatus() == BookStatus.AVAILABLE
                && book.get().getStockQuantity() >= quantity;
    }
}
