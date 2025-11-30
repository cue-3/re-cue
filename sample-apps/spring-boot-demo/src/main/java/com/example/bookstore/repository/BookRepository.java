package com.example.bookstore.repository;

import com.example.bookstore.model.Book;
import com.example.bookstore.model.Book.BookStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for Book entity.
 * 
 * Provides data access methods for books including search and filtering capabilities.
 */
@Repository
public interface BookRepository extends JpaRepository<Book, Long> {

    /**
     * Find a book by ISBN
     */
    Optional<Book> findByIsbn(String isbn);

    /**
     * Find books by author
     */
    List<Book> findByAuthorContainingIgnoreCase(String author);

    /**
     * Find books by title
     */
    List<Book> findByTitleContainingIgnoreCase(String title);

    /**
     * Find books by status
     */
    List<Book> findByStatus(BookStatus status);

    /**
     * Find available books in stock
     */
    @Query("SELECT b FROM Book b WHERE b.status = 'AVAILABLE' AND b.stockQuantity > 0")
    List<Book> findAvailableBooks();

    /**
     * Search books by title or author
     */
    @Query("SELECT b FROM Book b WHERE LOWER(b.title) LIKE LOWER(CONCAT('%', :searchTerm, '%')) " +
           "OR LOWER(b.author) LIKE LOWER(CONCAT('%', :searchTerm, '%'))")
    List<Book> searchBooks(@Param("searchTerm") String searchTerm);

    /**
     * Check if a book exists by ISBN
     */
    boolean existsByIsbn(String isbn);
}
