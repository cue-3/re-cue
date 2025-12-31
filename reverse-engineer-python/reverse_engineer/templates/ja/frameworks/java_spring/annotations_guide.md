## Spring Frameworkアノテーションガイド

### コアSpringアノテーション

#### コンポーネントスキャン
- **`@Component`** - Spring管理コンポーネントの汎用ステレオタイプ
- **`@Service`** - ビジネスロジック層
- **`@Repository`** - データアクセス層（DAO）
- **`@Controller`** - MVCコントローラー（ビューを返す）
- **`@RestController`** - REST APIコントローラー（JSON/XMLを返す）
  - `@Controller` + `@ResponseBody`の組み合わせ

#### 依存性注入
- **`@Autowired`** - 自動依存性注入
  - コンストラクタ注入（推奨）
  - セッター注入
  - フィールド注入
- **`@Qualifier`** - 複数の候補が存在する場合に注入するBeanを指定
- **`@Value`** - プロパティファイルから値を注入
- **`@ConfigurationProperties`** - タイプセーフな設定バインディング

### Web層アノテーション

#### リクエストマッピング
- **`@RequestMapping`** - ベースマッピングアノテーション
- **`@GetMapping`** - HTTP GETリクエスト
- **`@PostMapping`** - HTTP POSTリクエスト
- **`@PutMapping`** - HTTP PUTリクエスト
- **`@DeleteMapping`** - HTTP DELETEリクエスト
- **`@PatchMapping`** - HTTP PATCHリクエスト

#### リクエストパラメータ
- **`@PathVariable`** - URIパスから値を抽出
  ```java
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id)
  ```

- **`@RequestParam`** - クエリパラメータを抽出
  ```java
  @GetMapping("/search")
  public List<User> search(@RequestParam String name)
  ```

- **`@RequestBody`** - HTTPリクエストボディをオブジェクトにバインド
  ```java
  @PostMapping("/users")
  public User create(@RequestBody User user)
  ```

- **`@RequestHeader`** - HTTPヘッダー値を抽出
- **`@CookieValue`** - Cookie値を抽出

#### レスポンス処理
- **`@ResponseBody`** - 戻り値をレスポンスボディにシリアライズ
- **`@ResponseStatus`** - レスポンスのHTTPステータスコードを設定
- **`@ExceptionHandler`** - 特定の例外を処理

### セキュリティアノテーション

#### メソッドセキュリティ
- **`@EnableGlobalMethodSecurity`** - メソッドレベルのセキュリティを有効化
  ```java
  @EnableGlobalMethodSecurity(prePostEnabled = true)
  ```

- **`@PreAuthorize`** - メソッド実行前に認可をチェック
  ```java
  @PreAuthorize("hasRole('ADMIN')")
  @PreAuthorize("hasAuthority('USER_READ')")
  @PreAuthorize("#username == authentication.principal.username")
  ```

- **`@PostAuthorize`** - メソッド実行後に認可をチェック
- **`@Secured`** - ロールベースの認可（@PreAuthorizeよりシンプル）
  ```java
  @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
  ```

- **`@RolesAllowed`** - ロール認可のためのJSR-250アノテーション

### データ層アノテーション

#### JPA/Hibernate
- **`@Entity`** - クラスをJPAエンティティとしてマーク
- **`@Table`** - データベーステーブル名を指定
- **`@Id`** - 主キーフィールド
- **`@GeneratedValue`** - 主キーの自動生成
- **`@Column`** - カラムマッピングのカスタマイズ
- **`@OneToMany`, `@ManyToOne`, `@ManyToMany`** - リレーションシップの定義
- **`@Transactional`** - 宣言的トランザクション管理

#### Spring Data
- **`@Query`** - カスタムJPQLまたはSQLクエリを定義
- **`@Modifying`** - クエリを変更操作としてマーク
- **`@Repository`** - データアクセスの例外変換を有効化

### 設定アノテーション

#### Bean定義
- **`@Configuration`** - クラスを設定ソースとしてマーク
- **`@Bean`** - 設定クラス内でSpring Beanを定義
  ```java
  @Configuration
  public class AppConfig {
      @Bean
      public DataSource dataSource() {
          return new HikariDataSource();
      }
  }
  ```

#### プロパティ管理
- **`@PropertySource`** - ファイルからプロパティをロード
- **`@Profile`** - アクティブプロファイルに基づく条件付きBean登録
  ```java
  @Configuration
  @Profile("production")
  ```

#### 条件付きBean
- **`@ConditionalOnProperty`** - プロパティ値に基づいてBeanを有効化
- **`@ConditionalOnClass`** - クラスが存在する場合にBeanを有効化
- **`@ConditionalOnMissingBean`** - 他のBeanが存在しない場合にBeanを有効化

### バリデーションアノテーション

#### JSR-303/Jakartaバリデーション
- **`@Valid`** - メソッドパラメータ/戻り値でバリデーションをトリガー
- **`@NotNull`** - フィールドがnullでないことを検証
- **`@NotEmpty`** - 文字列/コレクションが空でないことを検証
- **`@NotBlank`** - 文字列がnullまたは空白でないことを検証
- **`@Size`** - 文字列/コレクションのサイズを検証
- **`@Min`, `@Max`** - 数値範囲の検証
- **`@Email`** - メールフォーマットの検証
- **`@Pattern`** - 正規表現パターンの検証

### 非同期処理とスケジューリング

#### 非同期処理
- **`@EnableAsync`** - 非同期メソッド実行を有効化
- **`@Async`** - メソッドを非同期実行用にマーク
  ```java
  @Async
  public CompletableFuture<Result> processAsync()
  ```

#### スケジュールタスク
- **`@EnableScheduling`** - スケジュールタスクサポートを有効化
- **`@Scheduled`** - メソッド実行をスケジュール
  ```java
  @Scheduled(cron = "0 0 * * * *")  // 毎時
  @Scheduled(fixedRate = 5000)       // 5秒ごと
  ```

### キャッシングアノテーション

- **`@EnableCaching`** - キャッシングサポートを有効化
- **`@Cacheable`** - メソッドの結果をキャッシュ
- **`@CacheEvict`** - キャッシュからエントリを削除
- **`@CachePut`** - メソッド実行に干渉せずにキャッシュを更新

### テストアノテーション

- **`@SpringBootTest`** - 統合テスト用に完全なアプリケーションコンテキストをロード
- **`@WebMvcTest`** - MVCコントローラーのテスト（スライステスト）
- **`@DataJpaTest`** - JPAリポジトリのテスト（スライステスト）
- **`@MockBean`** - SpringコンテキストにモックBeanを追加
- **`@Autowired` + `@MockBean`** - モック化された依存関係を注入

### 一般的なパターン

#### RESTコントローラーパターン
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

#### サービス層パターン
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

#### 設定パターン
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

### ベストプラクティス

1. **テスタビリティ向上のため、フィールド注入よりコンストラクタ注入を優先**
2. **REST APIには`@Controller` + `@ResponseBody`ではなく`@RestController`を使用**
3. **きめ細かいアクセス制御には`@PreAuthorize`でメソッドセキュリティを適用**
4. **`@Valid`とバリデーションアノテーションを使用して入力を検証**
5. **`@Transactional`はコントローラー層ではなくサービス層で使用**
6. **可能な限り手動Bean定義の代わりにSpring Bootの自動設定を活用**
7. **汎用的な`@RequestMapping`より特定のマッピングアノテーション（`@GetMapping`など）を使用**
8. **パフォーマンス向上のため、読み取り専用操作には`@Transactional(readOnly = true)`をマーク**