## Spring Framework Annotationen-Leitfaden

### Kern-Spring-Annotationen

#### Component Scanning
- **`@Component`** - Generisches Stereotyp für jede von Spring verwaltete Komponente
- **`@Service`** - Geschäftslogik-Schicht
- **`@Repository`** - Datenzugriffsschicht (DAO)
- **`@Controller`** - MVC-Controller (gibt Views zurück)
- **`@RestController`** - REST-API-Controller (gibt JSON/XML zurück)
  - Kombiniert `@Controller` + `@ResponseBody`

#### Dependency Injection
- **`@Autowired`** - Automatische Abhängigkeitsinjektion
  - Konstruktor-Injektion (empfohlen)
  - Setter-Injektion
  - Feld-Injektion
- **`@Qualifier`** - Spezifiziert, welche Bean injiziert werden soll, wenn mehrere Kandidaten existieren
- **`@Value`** - Injiziert Werte aus Properties-Dateien
- **`@ConfigurationProperties`** - Typsichere Konfigurationsbindung

### Web-Schicht-Annotationen

#### Request Mapping
- **`@RequestMapping`** - Basis-Mapping-Annotation
- **`@GetMapping`** - HTTP GET-Anfragen
- **`@PostMapping`** - HTTP POST-Anfragen
- **`@PutMapping`** - HTTP PUT-Anfragen
- **`@DeleteMapping`** - HTTP DELETE-Anfragen
- **`@PatchMapping`** - HTTP PATCH-Anfragen

#### Request-Parameter
- **`@PathVariable`** - Extrahiert Werte aus dem URI-Pfad
  ```java
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id)
  ```

- **`@RequestParam`** - Extrahiert Query-Parameter
  ```java
  @GetMapping("/search")
  public List<User> search(@RequestParam String name)
  ```

- **`@RequestBody`** - Bindet HTTP-Request-Body an Objekt
  ```java
  @PostMapping("/users")
  public User create(@RequestBody User user)
  ```

- **`@RequestHeader`** - Extrahiert HTTP-Header-Werte
- **`@CookieValue`** - Extrahiert Cookie-Werte

#### Response-Behandlung
- **`@ResponseBody`** - Serialisiert Rückgabewert in Response-Body
- **`@ResponseStatus`** - Setzt HTTP-Statuscode für Response
- **`@ExceptionHandler`** - Behandelt spezifische Ausnahmen

### Sicherheits-Annotationen

#### Methoden-Sicherheit
- **`@EnableGlobalMethodSecurity`** - Aktiviert Sicherheit auf Methodenebene
  ```java
  @EnableGlobalMethodSecurity(prePostEnabled = true)
  ```

- **`@PreAuthorize`** - Prüft Autorisierung vor Methodenausführung
  ```java
  @PreAuthorize("hasRole('ADMIN')")
  @PreAuthorize("hasAuthority('USER_READ')")
  @PreAuthorize("#username == authentication.principal.username")
  ```

- **`@PostAuthorize`** - Prüft Autorisierung nach Methodenausführung
- **`@Secured`** - Rollenbasierte Autorisierung (einfacher als @PreAuthorize)
  ```java
  @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
  ```

- **`@RolesAllowed`** - JSR-250-Annotation für Rollenautorisierung

### Datenschicht-Annotationen

#### JPA/Hibernate
- **`@Entity`** - Markiert Klasse als JPA-Entität
- **`@Table`** - Spezifiziert Datenbanktabellennamen
- **`@Id`** - Primärschlüssel-Feld
- **`@GeneratedValue`** - Automatisch generierter Primärschlüssel
- **`@Column`** - Anpassung der Spaltenzuordnung
- **`@OneToMany`, `@ManyToOne`, `@ManyToMany`** - Definiert Beziehungen
- **`@Transactional`** - Verwaltet Transaktionen deklarativ

#### Spring Data
- **`@Query`** - Definiert benutzerdefinierte JPQL- oder SQL-Abfragen
- **`@Modifying`** - Markiert Abfrage als modifizierende Operation
- **`@Repository`** - Aktiviert Exception-Übersetzung für Datenzugriff

### Konfigurations-Annotationen

#### Bean-Definition
- **`@Configuration`** - Markiert Klasse als Konfigurationsquelle
- **`@Bean`** - Definiert Spring-Bean in Konfigurationsklasse
  ```java
  @Configuration
  public class AppConfig {
      @Bean
      public DataSource dataSource() {
          return new HikariDataSource();
      }
  }
  ```

#### Property-Verwaltung
- **`@PropertySource`** - Lädt Properties aus Datei
- **`@Profile`** - Bedingte Bean-Registrierung basierend auf aktivem Profil
  ```java
  @Configuration
  @Profile("production")
  ```

#### Bedingte Beans
- **`@ConditionalOnProperty`** - Aktiviert Bean basierend auf Property-Wert
- **`@ConditionalOnClass`** - Aktiviert Bean, wenn Klasse vorhanden ist
- **`@ConditionalOnMissingBean`** - Aktiviert Bean, wenn keine andere Bean existiert

### Validierungs-Annotationen

#### JSR-303/Jakarta Validation
- **`@Valid`** - Löst Validierung bei Methodenparameter/Rückgabewert aus
- **`@NotNull`** - Feld darf nicht null sein
- **`@NotEmpty`** - String/Collection darf nicht leer sein
- **`@NotBlank`** - String darf nicht null oder Leerzeichen sein
- **`@Size`** - Validiert Größe von String/Collection
- **`@Min`, `@Max`** - Numerische Bereichsvalidierung
- **`@Email`** - E-Mail-Format-Validierung
- **`@Pattern`** - Regex-Muster-Validierung

### Async & Scheduling

#### Asynchrone Verarbeitung
- **`@EnableAsync`** - Aktiviert asynchrone Methodenausführung
- **`@Async`** - Markiert Methode für asynchrone Ausführung
  ```java
  @Async
  public CompletableFuture<Result> processAsync()
  ```

#### Geplante Aufgaben
- **`@EnableScheduling`** - Aktiviert Unterstützung für geplante Aufgaben
- **`@Scheduled`** - Plant Methodenausführung
  ```java
  @Scheduled(cron = "0 0 * * * *")  // Jede Stunde
  @Scheduled(fixedRate = 5000)       // Alle 5 Sekunden
  ```

### Caching-Annotationen

- **`@EnableCaching`** - Aktiviert Caching-Unterstützung
- **`@Cacheable`** - Cached Methodenergebnisse
- **`@CacheEvict`** - Entfernt Einträge aus dem Cache
- **`@CachePut`** - Aktualisiert Cache ohne Methodenausführung zu beeinträchtigen

### Test-Annotationen

- **`@SpringBootTest`** - Lädt vollständigen Anwendungskontext für Integrationstests
- **`@WebMvcTest`** - Testet MVC-Controller (Slice-Test)
- **`@DataJpaTest`** - Testet JPA-Repositories (Slice-Test)
- **`@MockBean`** - Fügt Mock-Bean zum Spring-Kontext hinzu
- **`@Autowired` + `@MockBean`** - Injiziert gemockte Abhängigkeiten

### Gängige Muster

#### REST-Controller-Muster
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

#### Service-Schicht-Muster
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

#### Konfigurations-Muster
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

1. **Bevorzugen Sie Konstruktor-Injektion** gegenüber Feld-Injektion für bessere Testbarkeit
2. **Verwenden Sie `@RestController`** für REST-APIs anstatt `@Controller` + `@ResponseBody`
3. **Wenden Sie Methoden-Sicherheit an** mit `@PreAuthorize` für feingranulare Zugriffskontrolle
4. **Validieren Sie Eingaben** mit `@Valid` und Validierungs-Annotationen
5. **Verwenden Sie `@Transactional`** auf Service-Ebene, nicht auf Controller-Ebene
6. **Nutzen Sie Spring Boot Auto-Konfiguration** anstatt manueller Bean-Definitionen, wenn möglich
7. **Verwenden Sie spezifische Mapping-Annotationen** (`@GetMapping`, etc.) anstatt generisches `@RequestMapping`
8. **Markieren Sie Nur-Lese-Operationen** mit `@Transactional(readOnly = true)` für bessere Performance