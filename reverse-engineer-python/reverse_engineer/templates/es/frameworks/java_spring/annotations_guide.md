## Guía de Anotaciones de Spring Framework

### Anotaciones Principales de Spring

#### Escaneo de Componentes
- **`@Component`** - Estereotipo genérico para cualquier componente gestionado por Spring
- **`@Service`** - Capa de lógica de negocio
- **`@Repository`** - Capa de acceso a datos (DAO)
- **`@Controller`** - Controlador MVC (devuelve vistas)
- **`@RestController`** - Controlador de API REST (devuelve JSON/XML)
  - Combina `@Controller` + `@ResponseBody`

#### Inyección de Dependencias
- **`@Autowired`** - Inyección automática de dependencias
  - Inyección por constructor (recomendada)
  - Inyección por setter
  - Inyección por campo
- **`@Qualifier`** - Especificar qué bean inyectar cuando existen múltiples candidatos
- **`@Value`** - Inyectar valores desde archivos de propiedades
- **`@ConfigurationProperties`** - Enlace de configuración con tipo seguro

### Anotaciones de la Capa Web

#### Mapeo de Peticiones
- **`@RequestMapping`** - Anotación base de mapeo
- **`@GetMapping`** - Peticiones HTTP GET
- **`@PostMapping`** - Peticiones HTTP POST
- **`@PutMapping`** - Peticiones HTTP PUT
- **`@DeleteMapping`** - Peticiones HTTP DELETE
- **`@PatchMapping`** - Peticiones HTTP PATCH

#### Parámetros de Petición
- **`@PathVariable`** - Extraer valores de la ruta URI
  ```java
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id)
  ```

- **`@RequestParam`** - Extraer parámetros de consulta
  ```java
  @GetMapping("/search")
  public List<User> search(@RequestParam String name)
  ```

- **`@RequestBody`** - Enlazar el cuerpo de la petición HTTP a un objeto
  ```java
  @PostMapping("/users")
  public User create(@RequestBody User user)
  ```

- **`@RequestHeader`** - Extraer valores de encabezados HTTP
- **`@CookieValue`** - Extraer valores de cookies

#### Manejo de Respuestas
- **`@ResponseBody`** - Serializar el valor de retorno al cuerpo de la respuesta
- **`@ResponseStatus`** - Establecer el código de estado HTTP para la respuesta
- **`@ExceptionHandler`** - Manejar excepciones específicas

### Anotaciones de Seguridad

#### Seguridad a Nivel de Método
- **`@EnableGlobalMethodSecurity`** - Habilitar seguridad a nivel de método
  ```java
  @EnableGlobalMethodSecurity(prePostEnabled = true)
  ```

- **`@PreAuthorize`** - Verificar autorización antes de la ejecución del método
  ```java
  @PreAuthorize("hasRole('ADMIN')")
  @PreAuthorize("hasAuthority('USER_READ')")
  @PreAuthorize("#username == authentication.principal.username")
  ```

- **`@PostAuthorize`** - Verificar autorización después de la ejecución del método
- **`@Secured`** - Autorización basada en roles (más simple que @PreAuthorize)
  ```java
  @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
  ```

- **`@RolesAllowed`** - Anotación JSR-250 para autorización por roles

### Anotaciones de la Capa de Datos

#### JPA/Hibernate
- **`@Entity`** - Marcar clase como entidad JPA
- **`@Table`** - Especificar nombre de la tabla de base de datos
- **`@Id`** - Campo de clave primaria
- **`@GeneratedValue`** - Auto-generar clave primaria
- **`@Column`** - Personalizar mapeo de columna
- **`@OneToMany`, `@ManyToOne`, `@ManyToMany`** - Definir relaciones
- **`@Transactional`** - Gestionar transacciones declarativamente

#### Spring Data
- **`@Query`** - Definir consultas JPQL o SQL personalizadas
- **`@Modifying`** - Marcar consulta como operación de modificación
- **`@Repository`** - Habilitar traducción de excepciones para acceso a datos

### Anotaciones de Configuración

#### Definición de Beans
- **`@Configuration`** - Marcar clase como fuente de configuración
- **`@Bean`** - Definir bean de Spring en clase de configuración
  ```java
  @Configuration
  public class AppConfig {
      @Bean
      public DataSource dataSource() {
          return new HikariDataSource();
      }
  }
  ```

#### Gestión de Propiedades
- **`@PropertySource`** - Cargar propiedades desde archivo
- **`@Profile`** - Registro condicional de bean basado en perfil activo
  ```java
  @Configuration
  @Profile("production")
  ```

#### Beans Condicionales
- **`@ConditionalOnProperty`** - Habilitar bean basado en valor de propiedad
- **`@ConditionalOnClass`** - Habilitar bean si la clase está presente
- **`@ConditionalOnMissingBean`** - Habilitar bean si no existe otro bean

### Anotaciones de Validación

#### JSR-303/Jakarta Validation
- **`@Valid`** - Activar validación en parámetro/valor de retorno del método
- **`@NotNull`** - El campo no puede ser null
- **`@NotEmpty`** - String/Collection no puede estar vacío
- **`@NotBlank`** - String no puede ser null o espacios en blanco
- **`@Size`** - Validar tamaño de String/Collection
- **`@Min`, `@Max`** - Validación de rango numérico
- **`@Email`** - Validación de formato de email
- **`@Pattern`** - Validación de patrón regex

### Procesamiento Asíncrono y Programación

#### Procesamiento Asíncrono
- **`@EnableAsync`** - Habilitar ejecución asíncrona de métodos
- **`@Async`** - Marcar método para ejecución asíncrona
  ```java
  @Async
  public CompletableFuture<Result> processAsync()
  ```

#### Tareas Programadas
- **`@EnableScheduling`** - Habilitar soporte para tareas programadas
- **`@Scheduled`** - Programar ejecución de método
  ```java
  @Scheduled(cron = "0 0 * * * *")  // Cada hora
  @Scheduled(fixedRate = 5000)       // Cada 5 segundos
  ```

### Anotaciones de Caché

- **`@EnableCaching`** - Habilitar soporte de caché
- **`@Cacheable`** - Cachear resultados de método
- **`@CacheEvict`** - Eliminar entradas del caché
- **`@CachePut`** - Actualizar caché sin interferir con la ejecución del método

### Anotaciones de Pruebas

- **`@SpringBootTest`** - Cargar contexto completo de aplicación para pruebas de integración
- **`@WebMvcTest`** - Probar controladores MVC (prueba segmentada)
- **`@DataJpaTest`** - Probar repositorios JPA (prueba segmentada)
- **`@MockBean`** - Agregar bean simulado al contexto de Spring
- **`@Autowired` + `@MockBean`** - Inyectar dependencias simuladas

### Patrones Comunes

#### Patrón de Controlador REST
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

#### Patrón de Capa de Servicio
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

#### Patrón de Configuración
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

### Mejores Prácticas

1. **Preferir Inyección por Constructor** sobre inyección por campo para mejor testabilidad
2. **Usar `@RestController`** para APIs REST en lugar de `@Controller` + `@ResponseBody`
3. **Aplicar seguridad a nivel de método** con `@PreAuthorize` para control de acceso detallado
4. **Validar entrada** usando `@Valid` y anotaciones de validación
5. **Usar `@Transactional`** en la capa de servicio, no en la capa de controlador
6. **Aprovechar la auto-configuración de Spring Boot** en lugar de definiciones manuales de beans cuando sea posible
7. **Usar anotaciones de mapeo específicas** (`@GetMapping`, etc.) sobre `@RequestMapping` genérico
8. **Marcar operaciones de solo lectura** con `@Transactional(readOnly = true)` para mejorar el rendimiento