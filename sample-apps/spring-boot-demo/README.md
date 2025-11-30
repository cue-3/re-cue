# Bookstore API - Sample Spring Boot Application

A clean, well-structured Spring Boot REST API for demonstration purposes with RE-cue VSCode extension.

## Features

- **RESTful API** for book and order management
- **Spring Data JPA** with H2 in-memory database
- **Bean Validation** for request validation
- **Lombok** for reducing boilerplate code
- **Comprehensive documentation** with JavaDoc comments
- **Service layer** with business logic
- **Repository layer** with custom queries
- **Entity relationships** (One-to-Many, Many-to-One)

## Architecture

```
src/main/java/com/example/bookstore/
├── BookstoreApplication.java       # Main application class
├── controller/                     # REST Controllers
│   ├── BookController.java         # Book management endpoints
│   └── OrderController.java        # Order management endpoints
├── service/                        # Business logic layer
│   ├── BookService.java           # Book operations
│   └── OrderService.java          # Order operations
├── repository/                     # Data access layer
│   ├── BookRepository.java        # Book data access
│   └── OrderRepository.java       # Order data access
└── model/                         # Domain entities
    ├── Book.java                  # Book entity
    ├── Order.java                 # Order entity
    └── OrderItem.java             # Order item entity
```

## API Endpoints

### Books
- `GET /api/books` - Get all books
- `GET /api/books/{id}` - Get book by ID
- `GET /api/books/isbn/{isbn}` - Get book by ISBN
- `GET /api/books/search?q={query}` - Search books
- `GET /api/books/available` - Get available books
- `POST /api/books` - Create a new book
- `PUT /api/books/{id}` - Update a book
- `PATCH /api/books/{id}/stock?quantity={qty}` - Update stock
- `DELETE /api/books/{id}` - Delete a book
- `GET /api/books/{id}/available?quantity={qty}` - Check availability

### Orders
- `GET /api/orders` - Get all orders
- `GET /api/orders/{id}` - Get order by ID
- `GET /api/orders/customer?email={email}` - Get customer orders
- `GET /api/orders/status/{status}` - Get orders by status
- `GET /api/orders/recent` - Get recent orders
- `POST /api/orders` - Create a new order
- `PATCH /api/orders/{id}/status?status={status}` - Update order status
- `POST /api/orders/{id}/cancel` - Cancel an order

## Running the Application

```bash
# Build the application
mvn clean install

# Run the application
mvn spring-boot:run

# Access the application
http://localhost:8080

# Access H2 Console (for database inspection)
http://localhost:8080/h2-console
JDBC URL: jdbc:h2:mem:bookstoredb
Username: sa
Password: (leave blank)
```

## Sample Data

Create sample books:
```bash
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "price": 44.99,
    "description": "A Handbook of Agile Software Craftsmanship",
    "stockQuantity": 10,
    "publishedYear": 2008
  }'
```

## Using with RE-cue Extension

1. Open this project in VS Code
2. Install the RE-cue extension
3. Right-click on any file and select "RE-cue: Analyze File"
4. Hover over endpoints, models, or services to see documentation
5. View analysis results in the RE-cue side panel
6. Generate comprehensive documentation with "RE-cue: Generate All Documentation"

## Technologies

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- H2 Database
- Lombok
- Bean Validation
- Maven
