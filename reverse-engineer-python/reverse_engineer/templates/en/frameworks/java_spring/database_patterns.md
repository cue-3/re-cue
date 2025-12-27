## Database Access Patterns - Java Spring

### JPA/Hibernate Entity Mapping

#### Basic Entity
```java
import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 100)
    private String email;
    
    @Column(nullable = false)
    private String password;
    
    @Column(name = "first_name", length = 50)
    private String firstName;
    
    @Column(name = "last_name", length = 50)
    private String lastName;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // Getters and setters
}
```

#### Entity Relationships
```java
// One-to-Many
@Entity
@Table(name = "posts")
public class Post {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String content;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;
    
    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Comment> comments = new ArrayList<>();
    
    // Helper method for bidirectional relationship
    public void addComment(Comment comment) {
        comments.add(comment);
        comment.setPost(this);
    }
    
    public void removeComment(Comment comment) {
        comments.remove(comment);
        comment.setPost(null);
    }
}

// Many-to-One
@Entity
@Table(name = "comments")
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String content;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id", nullable = false)
    private Post post;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
}

// Many-to-Many
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToMany
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();
}

@Entity
@Table(name = "roles")
public class Role {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String name;
    
    @ManyToMany(mappedBy = "roles")
    private Set<User> users = new HashSet<>();
}
```

### Spring Data JPA Repository

#### Basic Repository
```java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Method name queries (automatically implemented)
    Optional<User> findByEmail(String email);
    List<User> findByLastName(String lastName);
    List<User> findByFirstNameAndLastName(String firstName, String lastName);
    boolean existsByEmail(String email);
    long countByLastName(String lastName);
    void deleteByEmail(String email);
    
    // Using keywords
    List<User> findByCreatedAtAfter(LocalDateTime date);
    List<User> findByEmailContaining(String emailPart);
    List<User> findByFirstNameIgnoreCase(String firstName);
    List<User> findByLastNameOrderByFirstNameAsc(String lastName);
}
```

#### Custom Queries with @Query
```java
@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    
    // JPQL query
    @Query("SELECT p FROM Post p WHERE p.author.email = :email")
    List<Post> findPostsByAuthorEmail(@Param("email") String email);
    
    // Native SQL query
    @Query(value = "SELECT * FROM posts WHERE MATCH(title, content) AGAINST (?1)", 
           nativeQuery = true)
    List<Post> fullTextSearch(String searchTerm);
    
    // Projection with constructor expression
    @Query("SELECT new com.example.dto.PostSummary(p.id, p.title, p.author.email, SIZE(p.comments)) " +
           "FROM Post p WHERE p.createdAt > :date")
    List<PostSummary> findRecentPostSummaries(@Param("date") LocalDateTime date);
    
    // Modifying query
    @Modifying
    @Query("UPDATE Post p SET p.viewCount = p.viewCount + 1 WHERE p.id = :id")
    int incrementViewCount(@Param("id") Long id);
    
    // Delete query
    @Modifying
    @Query("DELETE FROM Post p WHERE p.createdAt < :date")
    int deleteOldPosts(@Param("date") LocalDateTime date);
    
    // Pagination and sorting
    @Query("SELECT p FROM Post p WHERE p.published = true")
    Page<Post> findPublishedPosts(Pageable pageable);
}
```

#### Specifications for Dynamic Queries
```java
import org.springframework.data.jpa.domain.Specification;

public class PostSpecifications {
    
    public static Specification<Post> hasAuthor(User author) {
        return (root, query, cb) -> cb.equal(root.get("author"), author);
    }
    
    public static Specification<Post> titleContains(String keyword) {
        return (root, query, cb) -> cb.like(
            cb.lower(root.get("title")), 
            "%" + keyword.toLowerCase() + "%"
        );
    }
    
    public static Specification<Post> createdAfter(LocalDateTime date) {
        return (root, query, cb) -> cb.greaterThan(root.get("createdAt"), date);
    }
    
    public static Specification<Post> isPublished() {
        return (root, query, cb) -> cb.isTrue(root.get("published"));
    }
}

// Repository with Specification support
public interface PostRepository extends JpaRepository<Post, Long>, 
                                       JpaSpecificationExecutor<Post> {
}

// Usage in service
@Service
public class PostService {
    @Autowired
    private PostRepository postRepository;
    
    public List<Post> searchPosts(String keyword, LocalDateTime after, User author) {
        Specification<Post> spec = Specification.where(
            PostSpecifications.isPublished()
        );
        
        if (keyword != null) {
            spec = spec.and(PostSpecifications.titleContains(keyword));
        }
        if (after != null) {
            spec = spec.and(PostSpecifications.createdAfter(after));
        }
        if (author != null) {
            spec = spec.and(PostSpecifications.hasAuthor(author));
        }
        
        return postRepository.findAll(spec);
    }
}
```

### Transaction Management

#### Declarative Transactions
```java
@Service
@Transactional
public class UserService {
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private AuditRepository auditRepository;
    
    // Read-only transaction (optimization)
    @Transactional(readOnly = true)
    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
    
    // Write transaction with rollback rules
    @Transactional(rollbackFor = Exception.class)
    public User createUser(User user) {
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new DuplicateEmailException(user.getEmail());
        }
        
        User savedUser = userRepository.save(user);
        
        // This will be part of the same transaction
        auditRepository.save(new AuditLog("USER_CREATED", savedUser.getId()));
        
        return savedUser;
    }
    
    // Multiple operations in one transaction
    @Transactional
    public void transferOwnership(Long postId, Long newOwnerId) {
        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new PostNotFoundException(postId));
        
        User newOwner = userRepository.findById(newOwnerId)
            .orElseThrow(() -> new UserNotFoundException(newOwnerId));
        
        post.setAuthor(newOwner);
        postRepository.save(post);
        
        auditRepository.save(new AuditLog("OWNERSHIP_TRANSFERRED", postId));
    }
    
    // Transaction with specific propagation
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logActivity(String activity) {
        // This runs in a separate transaction
        auditRepository.save(new AuditLog(activity));
    }
    
    // Transaction with timeout
    @Transactional(timeout = 5)
    public void longRunningOperation() {
        // Will rollback if takes more than 5 seconds
    }
}
```

#### Programmatic Transactions
```java
@Service
public class PaymentService {
    @Autowired
    private TransactionTemplate transactionTemplate;
    
    public Payment processPayment(PaymentRequest request) {
        return transactionTemplate.execute(status -> {
            try {
                // Business logic
                Payment payment = createPayment(request);
                updateAccount(request.getAccountId(), request.getAmount());
                return payment;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

### Query Optimization

#### Eager vs Lazy Loading
```java
@Entity
public class Post {
    // Lazy loading (default for @OneToMany and @ManyToMany)
    @OneToMany(mappedBy = "post", fetch = FetchType.LAZY)
    private List<Comment> comments;
    
    // Eager loading (default for @ManyToOne and @OneToOne)
    @ManyToOne(fetch = FetchType.EAGER)
    private User author;
}

// Fetch join to avoid N+1 problem
@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    @Query("SELECT p FROM Post p JOIN FETCH p.author WHERE p.id = :id")
    Optional<Post> findByIdWithAuthor(@Param("id") Long id);
    
    @Query("SELECT DISTINCT p FROM Post p LEFT JOIN FETCH p.comments WHERE p.id = :id")
    Optional<Post> findByIdWithComments(@Param("id") Long id);
    
    @EntityGraph(attributePaths = {"author", "comments"})
    Optional<Post> findWithDetailsById(Long id);
}
```

#### Batch Operations
```java
@Service
public class BatchService {
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private EntityManager entityManager;
    
    @Transactional
    public void batchInsert(List<User> users) {
        int batchSize = 50;
        
        for (int i = 0; i < users.size(); i++) {
            entityManager.persist(users.get(i));
            
            if (i % batchSize == 0 && i > 0) {
                entityManager.flush();
                entityManager.clear();
            }
        }
    }
    
    @Transactional
    public void batchUpdate(List<Long> userIds, String newStatus) {
        userRepository.flush();
        
        userRepository.findAllById(userIds).forEach(user -> {
            user.setStatus(newStatus);
        });
    }
}
```

#### Projections and DTOs
```java
// Interface projection
public interface UserSummary {
    String getEmail();
    String getFirstName();
    String getLastName();
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    List<UserSummary> findAllProjectedBy();
    UserSummary findProjectedById(Long id);
}

// Class projection (DTO)
public class PostDTO {
    private Long id;
    private String title;
    private String authorName;
    private int commentCount;
    
    // Constructor
    public PostDTO(Long id, String title, String authorName, int commentCount) {
        this.id = id;
        this.title = title;
        this.authorName = authorName;
        this.commentCount = commentCount;
    }
}

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    @Query("SELECT new com.example.dto.PostDTO(p.id, p.title, p.author.email, SIZE(p.comments)) " +
           "FROM Post p")
    List<PostDTO> findAllProjected();
}
```

### Connection Pooling

#### HikariCP Configuration
```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: dbuser
    password: dbpass
    driver-class-name: org.postgresql.Driver
    
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
      pool-name: HikariPool
      
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        show_sql: false
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true
```

#### Programmatic Configuration
```java
@Configuration
public class DataSourceConfig {
    
    @Bean
    @ConfigurationProperties("spring.datasource.hikari")
    public HikariConfig hikariConfig() {
        HikariConfig config = new HikariConfig();
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(5);
        config.setConnectionTimeout(20000);
        config.setIdleTimeout(300000);
        config.setMaxLifetime(1200000);
        config.setPoolName("HikariPool");
        return config;
    }
    
    @Bean
    public DataSource dataSource() {
        return new HikariDataSource(hikariConfig());
    }
}
```

### Raw SQL with JdbcTemplate

```java
@Repository
public class CustomUserRepository {
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    public List<User> findUsersByCustomQuery(String criteria) {
        String sql = "SELECT * FROM users WHERE status = ?";
        
        return jdbcTemplate.query(sql, new Object[]{criteria}, (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setEmail(rs.getString("email"));
            user.setFirstName(rs.getString("first_name"));
            user.setLastName(rs.getString("last_name"));
            return user;
        });
    }
    
    public int updateUserStatus(Long userId, String status) {
        String sql = "UPDATE users SET status = ? WHERE id = ?";
        return jdbcTemplate.update(sql, status, userId);
    }
    
    public Map<String, Object> getUserStats(Long userId) {
        String sql = "SELECT COUNT(*) as post_count, SUM(view_count) as total_views " +
                    "FROM posts WHERE author_id = ?";
        return jdbcTemplate.queryForMap(sql, userId);
    }
}
```

### Best Practices

1. **Use `@Transactional` at service layer**, not repository or controller
2. **Mark read-only operations** with `@Transactional(readOnly = true)`
3. **Avoid N+1 queries** - use JOIN FETCH or @EntityGraph
4. **Use projections** for read-only queries to reduce memory usage
5. **Batch operations** for bulk inserts/updates
6. **Configure connection pooling** appropriately for your load
7. **Use Specifications** for complex, dynamic queries
8. **Lazy load by default** - fetch eagerly only when needed
9. **Index frequently queried columns** in the database
10. **Monitor query performance** with hibernate.show_sql and explain plans

### Common Patterns

#### Repository Pattern Extension
```java
@Repository
public class UserRepositoryImpl implements UserRepositoryCustom {
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public List<User> findByComplexCriteria(SearchCriteria criteria) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> user = query.from(User.class);
        
        List<Predicate> predicates = new ArrayList<>();
        
        if (criteria.getEmail() != null) {
            predicates.add(cb.like(user.get("email"), "%" + criteria.getEmail() + "%"));
        }
        
        if (criteria.getMinAge() != null) {
            predicates.add(cb.greaterThanOrEqualTo(user.get("age"), criteria.getMinAge()));
        }
        
        query.where(predicates.toArray(new Predicate[0]));
        
        return entityManager.createQuery(query)
            .setMaxResults(criteria.getLimit())
            .getResultList();
    }
}
```

#### Audit Entity Base Class
```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class AuditableEntity {
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @CreatedBy
    @Column(name = "created_by", updatable = false)
    private String createdBy;
    
    @LastModifiedBy
    @Column(name = "updated_by")
    private String updatedBy;
}

// Enable JPA Auditing
@Configuration
@EnableJpaAuditing
public class JpaConfig {
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
            .map(SecurityContext::getAuthentication)
            .map(Authentication::getName);
    }
}
```
