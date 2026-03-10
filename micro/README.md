# 📚 BookStore Microservices Architecture

## Overview
This project is a microservices-based implementation of the BookStore application, decomposed from the monolithic architecture. It consists of 11 backend services + 1 API gateway with a web UI frontend.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY + WEB UI                              │
│                           (Port: 8000)                                       │
│                       Django Web UI Templates + Proxy                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────┐             ┌─────────────┐
│   staff     │            │  customer   │             │   catalog   │
│  service    │            │   service   │             │   service   │
│  (8001)     │            │   (8003)    │             │   (8004)    │
└─────────────┘            └─────────────┘             └─────────────┘
     │                              │                              │
     ▼                              │                              │
┌─────────────┐                     │                              │
│  manager    │                     │                              │
│  service    │                     │                              │
│  (8002)     │                     │                              │
└─────────────┘                     │                              │
                                    │                              │
                                    ▼                              ▼
                           ┌─────────────┐             ┌─────────────┐
                           │    cart     │◄────────────│    book     │
                           │   service   │             │   service   │
                           │   (8006)    │             │   (8005)    │
                           └─────────────┘             └─────────────┘
                                    │
                                    ▼
                           ┌─────────────┐
                           │   order     │
                           │   service   │
                           │   (8007)    │
                           └─────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │    ship     │ │     pay     │ │   comment   │
            │   service   │ │   service   │ │    rate     │
            │   (8008)    │ │   (8009)    │ │   (8010)    │
            └─────────────┘ └─────────────┘ └─────────────┘
                                                    │
                                                    ▼
                                          ┌─────────────┐
                                          │ recommender │
                                          │  AI service │
                                          │   (8011)    │
                                          └─────────────┘
```

## Services

| Service | Port | Description | Database |
|---------|------|-------------|----------|
| api-gateway | 8000 | Routes requests + Web UI | SQLite (sessions) |
| staff-service | 8001 | Staff authentication & management | staff_db |
| manager-service | 8002 | Admin/manager operations | manager_db |
| customer-service | 8003 | Customer auth & profile | customer_db |
| catalog-service | 8004 | Categories, Authors, Publishers | catalog_db |
| book-service | 8005 | Book CRUD & inventory | book_db |
| cart-service | 8006 | Shopping cart operations | cart_db |
| order-service | 8007 | Order processing | order_db |
| ship-service | 8008 | Shipping management | ship_db |
| pay-service | 8009 | Payment processing | pay_db |
| comment-rate-service | 8010 | Ratings & reviews | comment_db |
| recommender-ai-service | 8011 | AI-based recommendations | recommender_db |

## Quick Start

### Prerequisites
- Python 3.10+
- MySQL 8.0+ (running on localhost:3306)
- pip

### Database Setup

Ensure MySQL is running and create the databases:

```bash
mysql -u root -p < sql/init_databases.sql
```

### Running All Services (Recommended)

Use `run_local.py` to start all 12 services simultaneously with color-coded output:

```bash
cd micro

# First run (installs dependencies for each service)
python run_local.py

# Subsequent runs (skip dependency installation - faster)
python run_local.py --fast
```

### Seed Sample Data

After all services are running, open a new terminal and run:

```bash
cd micro
python seed_data.py
```

This creates: 3 staff, 6 categories, 5 authors, 4 publishers, 10 books, 3 customers, shipping methods/statuses, payment methods/statuses.

### Access the Application

After starting all services:
- **Web UI**: http://localhost:8000
- **API Gateway**: http://localhost:8000/api/

### Test Accounts

| Type | Username/Email | Password |
|------|---------------|----------|
| Customer | customer1 | pass123 |
| Admin | admin@bookstore.com | admin123 |
| Staff | staff1@bookstore.com | staff123 |
| Manager | manager1@bookstore.com | manager123 |

## Functional Requirements

### Customer
- ✅ Register / Login / Logout
- ✅ Browse book catalog (search, filter by category/author)
- ✅ View book details
- ✅ Rate books (1-5 stars)
- ✅ Write reviews
- ✅ Manage shopping cart (add/update/remove/clear)
- ✅ Checkout (select address, payment method, shipping method)
- ✅ Place orders
- ✅ View order history & order details
- ✅ Track order status
- ✅ Cancel orders
- ✅ Manage profile (name, phone)
- ✅ Manage delivery addresses (add/edit/delete)
- ✅ Get book recommendations

### Staff
- ✅ Staff login / logout
- ✅ Dashboard with statistics
- ✅ Add new books
- ✅ Edit book information
- ✅ Manage inventory (view stock, update quantities)
- ✅ Import stock
- ✅ View and manage orders
- ✅ Update order status

### Payment System
- ✅ Multiple payment methods
- ✅ Create payment for orders
- ✅ Process payments

### Shipping System
- ✅ Multiple shipping methods
- ✅ Calculate shipping fees
- ✅ Create shipments for orders
- ✅ Track shipments

### Recommendation Engine
- ✅ Get trending books
- ✅ Get best-rated books
- ✅ Get similar books
- ✅ Personalized recommendations

## API Documentation

### Gateway Routing Pattern
All API calls go through the gateway at port 8000:
```
GET http://localhost:8000/api/{service}/{path}
    → Forwards to: http://localhost:{port}/api/{path}
```

### Inter-Service Communication

```
customer-service ──HTTP──► cart-service (create cart on registration)
order-service ──HTTP──► pay-service (process payment)
order-service ──HTTP──► ship-service (create shipment)
order-service ──HTTP──► book-service (update inventory)
order-service ──HTTP──► cart-service (deactivate cart)
comment-rate-service ──HTTP──► book-service (update book rating)
recommender-ai-service ──HTTP──► book-service, order-service (fetch data)
```

## Technology Stack

- **Framework**: Django REST Framework
- **Databases**: MySQL (independent per service)
- **Containerization**: Docker & Docker Compose
- **Communication**: REST API (synchronous HTTP)
- **Authentication**: JWT tokens

## Project Structure

```
micro/
├── run_local.py              # Start all services
├── seed_data.py              # Seed sample data
├── sql/                      # Database initialization SQL
├── api-gateway/              # Gateway + Web UI (port 8000)
├── staff-service/            # (port 8001)
├── manager-service/          # (port 8002)
├── customer-service/         # (port 8003)
├── catalog-service/          # (port 8004)
├── book-service/             # (port 8005)
├── cart-service/             # (port 8006)
├── order-service/            # (port 8007)
├── ship-service/             # (port 8008)
├── pay-service/              # (port 8009)
├── comment-rate-service/     # (port 8010)
└── recommender-ai-service/   # (port 8011)
```

## License

MIT License
