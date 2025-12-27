## Spring Framework Annotations Guide

### Core Spring Annotations

#### Component Scanning
- **`@Component`** - Generic stereotype for any Spring-managed component
- **`@Service`** - Business logic layer
- **`@Repository`** - Data access layer (DAO)
- **`@Controller`** - MVC controller (returns views)
- **`@RestController`** - REST API controller (returns JSON/XML)
  - Combines `@Controller` + `@ResponseBody`

#### Dependency Injection
- **`@Autowired`** - Automatic dependency injection
  - Constructor injection (recommended)
  - Setter injection
  - Field injection
- **`@Qualifier`** - Specify which bean to inject when multiple candidates exist
- **`@Value`** - Inject values from properties files
- **`@ConfigurationProperties`** - Type-safe configuration binding

### Web Layer Annotations

#### Request Mapping
- **`@RequestMapping`** - Base mapping annotation
- **`@GetMapping`** - HTTP GET requests
- **`@PostMapping`** - HTTP POST requests
- **`@PutMapping`** - HTTP PUT requests
- **`@DeleteMapping`** - HTTP DELETE requests
- **`@PatchMapping`** - HTTP PATCH requests

#### Request Parameters
- **`@PathVariable`** - Extract values from URI path
  ```java
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id)
  ```

- **`@RequestParam`** - Extract query parameters
  ```java
  @GetMapping("/search")
  public List<User> search(@RequestParam String name)
  ```

- **`@RequestBody`** - Bind HTTP request body to object
  ```java
  @PostMapping("/users")
  public User create(@RequestBody User user)
  ```

- **`@RequestHeader`** - Extract HTTP header values
- **`@CookieValue`** - Extract cookie values

#### Response Handling
- **`@ResponseBody`** - Serialize return value to response body
- **`@ResponseStatus`** - Set HTTP status code for response
- **`@ExceptionHandler`** - Handle specific exceptions

### Security Annotations

#### Method Security
- **`@EnableGlobalMethodSecurity`** - Enable method-level security
  ```java
  @EnableGlobalMethodSecurity(prePostEnabled = true)
  ```

- **`@PreAuthorize`** - Check authorization before method execution
  ```java
  @PreAuthorize("hasRole('ADMIN')")
  @PreAuthorize("hasAuthority('USER_READ')")
  @PreAuthorize("#username == authentication.principal.username")
  ```

- **`@PostAuthorize`** - Check authorization after method execution
- **`@Secured`** - Role-based authorization (simpler than @PreAuthorize)
  ```java
  @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
  ```

- **`@RolesAllowed`** - JSR-250 annotation for role authorization

### Data Layer Annotations

#### JPA/Hibernate
- **`@Entity`** - Mark class as JPA entity
- **`@Table`** - Specify database table name
- **`@Id`** - Primary key field
- **`@GeneratedValue`** - Auto-generate primary key
- **`@Column`** - Customize column mapping
- **`@OneToMany`, `@ManyToOne`, `@ManyToMany`** - Define relationships
- **`@Transactional`** - Manage transactions declaratively

#### Spring Data
- **`@Query`** - Define custom JPQL or SQL queries
- **`@Modifying`** - Mark query as modifying operation
- **`@Repository`** - Enable exception translation for data access

### Configuration Annotations

#### Bean Definition
- **`@Configuration`** - Mark class as configuration source
- **`@Bean`** - Define Spring bean in configuration class
  ```java
  @Configuration
  public class AppConfig {
      @Bean
      public DataSource dataSource() {
          return new HikariDataSource();
      }
  }
  ```

#### Property Management
- **`@PropertySource`** - Load properties from file
- **`@Profile`** - Conditional bean registration based on active profile
  ```java
  @Configuration
  @Profile("production")
  ```

#### Conditional Beans
- **`@ConditionalOnProperty`** - Enable bean based on property value
- **`@ConditionalOnClass`** - Enable bean if class is present
- **`@ConditionalOnMissingBean`** - Enable bean if no other bean exists

### Validation Annotations

#### JSR-303/Jakarta Validation
- **`@Valid`** - Trigger validation on method parameter/return value
- **`@NotNull`** - Field cannot be null
- **`@NotEmpty`** - String/Collection cannot be empty
- **`@NotBlank`** - String cannot be null or whitespace
- **`@Size`** - Validate size of String/Collection
- **`@Min`, `@Max`** - Numeric range validation
- **`@Email`** - Email format validation
- **`@Pattern`** - Regex pattern validation

### Async & Scheduling

#### Asynchronous Processing
- **`@EnableAsync`** - Enable async method execution
- **`@Async`** - Mark method for asynchronous execution
  ```java
  @Async
  public CompletableFuture<Result> processAsync()
  ```

#### Scheduled Tasks
- **`@EnableScheduling`** - Enable scheduled task support
- **`@Scheduled`** - Schedule method execution
  ```java
  @Scheduled(cron = "0 0 * * * *")  // Every hour
  @Scheduled(fixedRate = 5000)       // Every 5 seconds
  ```

### Caching Annotations

- **`@EnableCaching`** - Enable caching support
- **`@Cacheable`** - Cache method results
- **`@CacheEvict`** - Remove entries from cache
- **`@CachePut`** - Update cache without interfering with method execution

### Testing Annotations

- **`@SpringBootTest`** - Load full application context for integration tests
- **`@WebMvcTest`** - Test MVC controllers (sliced test)
- **`@DataJpaTest`** - Test JPA repositories (sliced test)
- **`@MockBean`** - Add mock bean to Spring context
- **`@Autowired` + `@MockBean`** - Inject mocked dependencies

### Common Patterns

#### REST Controller Pattern
```java
@RestController
@RequestMapping("/api/users")
@Validated
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(userService.create(user));
    }
}
```

#### Service Layer Pattern
```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Cacheable("users")
    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
    
    @CacheEvict(value = "users", allEntries = true)
    public User create(User user) {
        return userRepository.save(user);
    }
}
```

#### Configuration Pattern
```java
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .build();
    }
}
```

### Best Practices

1. **Prefer Constructor Injection** over field injection for better testability
2. **Use `@RestController`** for REST APIs instead of `@Controller` + `@ResponseBody`
3. **Apply method security** with `@PreAuthorize` for fine-grained access control
4. **Validate input** using `@Valid` and validation annotations
5. **Use `@Transactional`** at service layer, not controller layer
6. **Leverage Spring Boot auto-configuration** instead of manual bean definitions when possible
7. **Use specific mapping annotations** (`@GetMapping`, etc.) over generic `@RequestMapping`
8. **Mark read-only operations** with `@Transactional(readOnly = true)` for performance
