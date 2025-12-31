## Guide des Annotations Spring Framework

### Annotations Spring Principales

#### Balayage de Composants
- **`@Component`** - Stéréotype générique pour tout composant géré par Spring
- **`@Service`** - Couche de logique métier
- **`@Repository`** - Couche d'accès aux données (DAO)
- **`@Controller`** - Contrôleur MVC (retourne des vues)
- **`@RestController`** - Contrôleur API REST (retourne JSON/XML)
  - Combine `@Controller` + `@ResponseBody`

#### Injection de Dépendances
- **`@Autowired`** - Injection automatique de dépendances
  - Injection par constructeur (recommandée)
  - Injection par setter
  - Injection par champ
- **`@Qualifier`** - Spécifier quel bean injecter quand plusieurs candidats existent
- **`@Value`** - Injecter des valeurs depuis les fichiers de propriétés
- **`@ConfigurationProperties`** - Liaison de configuration typée

### Annotations de la Couche Web

#### Mappage de Requêtes
- **`@RequestMapping`** - Annotation de mappage de base
- **`@GetMapping`** - Requêtes HTTP GET
- **`@PostMapping`** - Requêtes HTTP POST
- **`@PutMapping`** - Requêtes HTTP PUT
- **`@DeleteMapping`** - Requêtes HTTP DELETE
- **`@PatchMapping`** - Requêtes HTTP PATCH

#### Paramètres de Requête
- **`@PathVariable`** - Extraire des valeurs du chemin URI
  ```java
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id)
  ```

- **`@RequestParam`** - Extraire les paramètres de requête
  ```java
  @GetMapping("/search")
  public List<User> search(@RequestParam String name)
  ```

- **`@RequestBody`** - Lier le corps de la requête HTTP à un objet
  ```java
  @PostMapping("/users")
  public User create(@RequestBody User user)
  ```

- **`@RequestHeader`** - Extraire les valeurs d'en-tête HTTP
- **`@CookieValue`** - Extraire les valeurs de cookie

#### Gestion des Réponses
- **`@ResponseBody`** - Sérialiser la valeur de retour dans le corps de la réponse
- **`@ResponseStatus`** - Définir le code de statut HTTP pour la réponse
- **`@ExceptionHandler`** - Gérer des exceptions spécifiques

### Annotations de Sécurité

#### Sécurité au Niveau Méthode
- **`@EnableGlobalMethodSecurity`** - Activer la sécurité au niveau méthode
  ```java
  @EnableGlobalMethodSecurity(prePostEnabled = true)
  ```

- **`@PreAuthorize`** - Vérifier l'autorisation avant l'exécution de la méthode
  ```java
  @PreAuthorize("hasRole('ADMIN')")
  @PreAuthorize("hasAuthority('USER_READ')")
  @PreAuthorize("#username == authentication.principal.username")
  ```

- **`@PostAuthorize`** - Vérifier l'autorisation après l'exécution de la méthode
- **`@Secured`** - Autorisation basée sur les rôles (plus simple que @PreAuthorize)
  ```java
  @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
  ```

- **`@RolesAllowed`** - Annotation JSR-250 pour l'autorisation par rôle

### Annotations de la Couche de Données

#### JPA/Hibernate
- **`@Entity`** - Marquer la classe comme entité JPA
- **`@Table`** - Spécifier le nom de la table de base de données
- **`@Id`** - Champ de clé primaire
- **`@GeneratedValue`** - Générer automatiquement la clé primaire
- **`@Column`** - Personnaliser le mappage de colonne
- **`@OneToMany`, `@ManyToOne`, `@ManyToMany`** - Définir les relations
- **`@Transactional`** - Gérer les transactions de manière déclarative

#### Spring Data
- **`@Query`** - Définir des requêtes JPQL ou SQL personnalisées
- **`@Modifying`** - Marquer la requête comme opération de modification
- **`@Repository`** - Activer la traduction d'exception pour l'accès aux données

### Annotations de Configuration

#### Définition de Bean
- **`@Configuration`** - Marquer la classe comme source de configuration
- **`@Bean`** - Définir un bean Spring dans une classe de configuration
  ```java
  @Configuration
  public class AppConfig {
      @Bean
      public DataSource dataSource() {
          return new HikariDataSource();
      }
  }
  ```

#### Gestion des Propriétés
- **`@PropertySource`** - Charger les propriétés depuis un fichier
- **`@Profile`** - Enregistrement conditionnel de bean basé sur le profil actif
  ```java
  @Configuration
  @Profile("production")
  ```

#### Beans Conditionnels
- **`@ConditionalOnProperty`** - Activer le bean selon la valeur d'une propriété
- **`@ConditionalOnClass`** - Activer le bean si la classe est présente
- **`@ConditionalOnMissingBean`** - Activer le bean si aucun autre bean n'existe

### Annotations de Validation

#### JSR-303/Jakarta Validation
- **`@Valid`** - Déclencher la validation sur le paramètre/valeur de retour de méthode
- **`@NotNull`** - Le champ ne peut pas être null
- **`@NotEmpty`** - La chaîne/collection ne peut pas être vide
- **`@NotBlank`** - La chaîne ne peut pas être null ou composée d'espaces blancs
- **`@Size`** - Valider la taille d'une chaîne/collection
- **`@Min`, `@Max`** - Validation de plage numérique
- **`@Email`** - Validation du format email
- **`@Pattern`** - Validation par motif regex

### Asynchrone et Planification

#### Traitement Asynchrone
- **`@EnableAsync`** - Activer l'exécution asynchrone de méthodes
- **`@Async`** - Marquer la méthode pour exécution asynchrone
  ```java
  @Async
  public CompletableFuture<Result> processAsync()
  ```

#### Tâches Planifiées
- **`@EnableScheduling`** - Activer le support des tâches planifiées
- **`@Scheduled`** - Planifier l'exécution de méthode
  ```java
  @Scheduled(cron = "0 0 * * * *")  // Toutes les heures
  @Scheduled(fixedRate = 5000)       // Toutes les 5 secondes
  ```

### Annotations de Cache

- **`@EnableCaching`** - Activer le support du cache
- **`@Cacheable`** - Mettre en cache les résultats de méthode
- **`@CacheEvict`** - Supprimer des entrées du cache
- **`@CachePut`** - Mettre à jour le cache sans interférer avec l'exécution de la méthode

### Annotations de Test

- **`@SpringBootTest`** - Charger le contexte d'application complet pour les tests d'intégration
- **`@WebMvcTest`** - Tester les contrôleurs MVC (test partiel)
- **`@DataJpaTest`** - Tester les dépôts JPA (test partiel)
- **`@MockBean`** - Ajouter un bean simulé au contexte Spring
- **`@Autowired` + `@MockBean`** - Injecter des dépendances simulées

### Modèles Courants

#### Modèle de Contrôleur REST
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

#### Modèle de Couche Service
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

#### Modèle de Configuration
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

### Meilleures Pratiques

1. **Préférer l'injection par constructeur** à l'injection par champ pour une meilleure testabilité
2. **Utiliser `@RestController`** pour les API REST au lieu de `@Controller` + `@ResponseBody`
3. **Appliquer la sécurité au niveau méthode** avec `@PreAuthorize` pour un contrôle d'accès fin
4. **Valider les entrées** en utilisant `@Valid` et les annotations de validation
5. **Utiliser `@Transactional`** au niveau de la couche service, pas au niveau contrôleur
6. **Exploiter l'auto-configuration Spring Boot** au lieu de définitions manuelles de beans quand c'est possible
7. **Utiliser des annotations de mappage spécifiques** (`@GetMapping`, etc.) plutôt que le générique `@RequestMapping`
8. **Marquer les opérations en lecture seule** avec `@Transactional(readOnly = true)` pour la performance