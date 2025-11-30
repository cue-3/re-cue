package com.example.bookstore.controller;

import com.example.bookstore.model.Book;
import com.example.bookstore.service.BookService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for book management operations.
 * 
 * Provides endpoints for CRUD operations on books, search functionality,
 * and inventory management.
 */
@RestController
@RequestMapping("/api/books")
@RequiredArgsConstructor
public class BookController {

    private final BookService bookService;

    /**
     * Get all books
     * 
     * @return List of all books
     */
    @GetMapping
    public ResponseEntity<List<Book>> getAllBooks() {
        List<Book> books = bookService.getAllBooks();
        return ResponseEntity.ok(books);
    }

    /**
     * Get a book by ID
     * 
     * @param id Book ID
     * @return Book details
     */
    @GetMapping("/{id}")
    public ResponseEntity<Book> getBookById(@PathVariable Long id) {
        return bookService.getBookById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get a book by ISBN
     * 
     * @param isbn Book ISBN
     * @return Book details
     */
    @GetMapping("/isbn/{isbn}")
    public ResponseEntity<Book> getBookByIsbn(@PathVariable String isbn) {
        return bookService.getBookByIsbn(isbn)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Search books by title or author
     * 
     * @param q Search query
     * @return List of matching books
     */
    @GetMapping("/search")
    public ResponseEntity<List<Book>> searchBooks(@RequestParam String q) {
        List<Book> books = bookService.searchBooks(q);
        return ResponseEntity.ok(books);
    }

    /**
     * Get available books
     * 
     * @return List of available books
     */
    @GetMapping("/available")
    public ResponseEntity<List<Book>> getAvailableBooks() {
        List<Book> books = bookService.getAvailableBooks();
        return ResponseEntity.ok(books);
    }

    /**
     * Create a new book
     * 
     * @param book Book details
     * @return Created book
     */
    @PostMapping
    public ResponseEntity<Book> createBook(@Valid @RequestBody Book book) {
        Book createdBook = bookService.createBook(book);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdBook);
    }

    /**
     * Update an existing book
     * 
     * @param id Book ID
     * @param book Updated book details
     * @return Updated book
     */
    @PutMapping("/{id}")
    public ResponseEntity<Book> updateBook(
            @PathVariable Long id,
            @Valid @RequestBody Book book) {
        try {
            Book updatedBook = bookService.updateBook(id, book);
            return ResponseEntity.ok(updatedBook);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Update book stock quantity
     * 
     * @param id Book ID
     * @param quantity New stock quantity
     * @return Updated book
     */
    @PatchMapping("/{id}/stock")
    public ResponseEntity<Book> updateStock(
            @PathVariable Long id,
            @RequestParam Integer quantity) {
        try {
            Book updatedBook = bookService.updateStock(id, quantity);
            return ResponseEntity.ok(updatedBook);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Delete a book
     * 
     * @param id Book ID
     * @return No content
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBook(@PathVariable Long id) {
        try {
            bookService.deleteBook(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Check if book is available
     * 
     * @param id Book ID
     * @param quantity Requested quantity
     * @return Availability status
     */
    @GetMapping("/{id}/available")
    public ResponseEntity<Boolean> checkAvailability(
            @PathVariable Long id,
            @RequestParam(defaultValue = "1") Integer quantity) {
        boolean isAvailable = bookService.isBookAvailable(id, quantity);
        return ResponseEntity.ok(isAvailable);
    }
}
