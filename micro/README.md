# Microservices Django - Book Store

This is the **Microservices Architecture** version of the Book Store Web System.

## Architecture Overview

```
micro/
├── gateway-service/        # API Gateway with Web UI (Port 8000)
│   ├── gateway_service/   # Django project settings
│   ├── gateway/           # Gateway app with views & service clients
│   └── templates/         # HTML templates for web interface
│
├── customer-service/       # Customer Management Service (Port 8001)
│   ├── customer_service/  # Django project settings
│   └── customers/         # Customer app with REST API
│
├── book-service/          # Book Catalog Service (Port 8002)
│   ├── book_service/      # Django project settings
│   └── books/             # Books app with REST API
│
├── cart-service/          # Shopping Cart Service (Port 8003)
│   ├── cart_service/      # Django project settings
│   └── cart/              # Cart app with REST API
│
└── sql/                   # Database initialization scripts
```

## Service Details

### Customer Service (Port 8001)
- **Database**: `bookstore_micro_customers`
- **Endpoints**:
  - `GET /api/customers/` - List all customers
  - `POST /api/customers/` - Create customer
  - `GET /api/customers/{id}/` - Get customer by ID
  - `POST /api/customers/register/` - Register new customer
  - `POST /api/customers/login/` - Authenticate customer
  - `GET /api/customers/{id}/verify/` - Verify customer exists
  - `GET /api/customers/health/` - Health check

### Book Service (Port 8002)
- **Database**: `bookstore_micro_books`
- **Endpoints**:
  - `GET /api/books/` - List all books (with ?search=query)
  - `POST /api/books/` - Create book
  - `GET /api/books/{id}/` - Get book by ID
  - `PUT /api/books/{id}/` - Update book
  - `DELETE /api/books/{id}/` - Delete book
  - `POST /api/books/{id}/update_stock/` - Update book stock
  - `GET /api/books/{id}/check_availability/` - Check availability
  - `GET /api/books/health/` - Health check

### Cart Service (Port 8003)
- **Database**: `bookstore_micro_carts`
- **Endpoints**:
  - `GET /api/cart/` - List all carts
  - `GET /api/cart/by_customer/?customer_id=X` - Get customer's cart
  - `POST /api/cart/add_item/` - Add item to cart
  - `POST /api/cart/update_item/` - Update item quantity
  - `POST /api/cart/remove_item/` - Remove item from cart
  - `POST /api/cart/clear/` - Clear all cart items
  - `GET /api/cart/health/` - Health check

## Setup Instructions

### 1. Create databases

```bash
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -p < sql/init_databases.sql
```

This creates three separate databases:
- `bookstore_micro_customers`
- `bookstore_micro_books`
- `bookstore_micro_carts`

### 2. Update database passwords

Edit settings.py in each service:
- `customer-service/customer_service/settings.py`
- `book-service/book_service/settings.py`
- `cart-service/cart_service/settings.py`

### 3. Setup each service (4 Terminals Required!)

**⚠️ IMPORTANT: Open 4 separate CMD/Terminal windows**

#### Terminal 1: Gateway Service (Port 8000) - WEB INTERFACE
```bash
cd gateway-service
py -m venv venv
venv\Scripts\activate  
pip install -r requirements.txt
py manage.py runserver 8000
```

#### Terminal 2: Customer Service (Port 8001)
```bash
cd customer-service
py -m venv venv
venv\Scripts\activate  
pip install -r requirements.txt
py manage.py migrate
py manage.py runserver 8001
```

#### Terminal 3: Book Service (Port 8002)
```bash
cd book-service
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py manage.py migrate
py manage.py runserver 8002
```

#### Terminal 4: Cart Service (Port 8003)
```bash
cd cart-service
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py manage.py migrate
py manage.py runserver 8003
```

### 4. Access the Application

**🌐 Web Interface: http://localhost:8000**

The Gateway Service provides the web UI and routes requests to microservices.

### 5. Test the services

```bash
# Health checks
curl http://localhost:8001/api/customers/health/
curl http://localhost:8002/api/books/health/
curl http://localhost:8003/api/cart/health/

# Get books
curl http://localhost:8002/api/books/

# Register customer
curl -X POST http://localhost:8001/api/customers/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"password123","password_confirm":"password123"}'

# Add to cart
curl -X POST http://localhost:8003/api/cart/add_item/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"book_id":1,"quantity":2}'
```

## Service Communication

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ Customer Service│     │  Book Service   │     │  Cart Service   │
│   (Port 8001)   │     │   (Port 8002)   │     │   (Port 8003)   │
│                 │     │                 │     │                 │
│  MySQL:         │     │  MySQL:         │     │  MySQL:         │
│  bookstore_     │     │  bookstore_     │     │  bookstore_     │
│  micro_customers│     │  micro_books    │     │  micro_carts    │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │       REST API        │
         │                       │◄──────────────────────┤
         │    REST API           │                       │
         │◄──────────────────────┴───────────────────────┤
         │                                               │
```

The Cart Service communicates with:
- Customer Service: To verify customer exists
- Book Service: To get book details and check stock

## Key Characteristics

| Characteristic | Description |
|----------------|-------------|
| Independent Deployment | Each service can be deployed separately |
| Independent Scaling | Services can scale based on load |
| Technology Freedom | Each service could use different tech stack |
| Fault Isolation | Failure in one service doesn't crash others |
| Data Ownership | Each service owns its database |

## Comparing to Other Architectures

| Aspect | Monolithic | Clean | Microservices |
|--------|------------|-------|---------------|
| Deployment Units | 1 | 1 | 3 |
| Databases | 1 | 1 | 3 |
| Network Calls | None | None | Inter-service REST |
| Complexity | Low | Medium | High |
| Team Scalability | Limited | Medium | High |

## Production Considerations

For production deployment, consider:
1. **API Gateway**: Use Kong, Nginx, or Traefik
2. **Service Discovery**: Consul or Kubernetes
3. **Load Balancing**: HAProxy or cloud load balancers
4. **Monitoring**: Prometheus + Grafana
5. **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
6. **Containerization**: Docker + Kubernetes
