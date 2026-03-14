# BookStore Microservices

A complete Online BookStore system built with **Microservices Architecture**. Twelve independent Django REST Framework services, each with its own MySQL database, communicate through REST APIs. An API Gateway acts as the single entry point with a simple web UI.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Prerequisites](#prerequisites)
4. [Quick Start (3 Steps)](#quick-start-3-steps)
5. [Running Locally — Step by Step](#running-locally--step-by-step)
6. [Running with Docker Compose](#running-with-docker-compose)
7. [Sample Accounts](#sample-accounts)
8. [API Reference](#api-reference)
9. [Workflow Walkthroughs](#workflow-walkthroughs)
10. [Service Communication Map](#service-communication-map)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
                         ┌────────────────────────────────────────────┐
                         │              Browser / Client               │
                         └───────────────────┬────────────────────────┘
                                             │ HTTP
                         ┌───────────────────▼────────────────────────┐
                         │          API Gateway  :8000                 │
                         │   (Django Template Web UI + REST proxy)     │
                         └──┬────┬───┬───┬───┬───┬───┬───┬───┬───┬───┘
                            │    │   │   │   │   │   │   │   │   │   │
              ┌─────────────┘    │   │   │   │   │   │   │   │   │   └──────────────┐
              │                  │   │   │   │   │   │   │   │   │                  │
      ┌───────▼──────┐   ┌───────▼───┐  │   │   │   │   │   │   │          ┌───────▼──────────┐
      │ staff-service│   │manager-svc│  │   │   │   │   │   │   │          │recommender-ai-svc│
      │    :8001     │   │   :8002   │  │   │   │   │   │   │   │          │      :8011       │
      │  staff_db    │   │manager_db │  │   │   │   │   │   │   │          │  recommender_db  │
      └──────────────┘   └───────────┘  │   │   │   │   │   │   │          └──────────────────┘
                                        │   │   │   │   │   │   │
                              ┌─────────▼─┐ │   │   │   │   │   └─────────────┐
                              │customer-  │ │   │   │   │   │                 │
                              │service    │ │   │   │   │   │        ┌────────▼──────┐
                              │:8003      │ │   │   │   │   │        │comment-rate-  │
                              │customer_db│ │   │   │   │   │        │service :8010  │
                              └───────────┘ │   │   │   │   │        │  comment_db   │
                                            │   │   │   │   │        └───────────────┘
                                   ┌────────▼─┐ │   │   │   └──────────────┐
                                   │catalog-  │ │   │   │                  │
                                   │service   │ │   │   │         ┌────────▼──────┐
                                   │:8004     │ │   │   │         │  pay-service  │
                                   │catalog_db│ │   │   │         │    :8009      │
                                   └──────────┘ │   │   │         │   pay_db      │
                                                │   │   │         └───────────────┘
                                       ┌────────▼─┐ │   └─────────────────┐
                                       │ book-    │ │                     │
                                       │ service  │ │            ┌────────▼──────┐
                                       │ :8005    │ │            │ ship-service  │
                                       │ book_db  │ │            │    :8008      │
                                       └──────────┘ │            │   ship_db     │
                                                    │            └───────────────┘
                                           ┌────────▼──┐
                                           │ cart-     │
                                           │ service   │
                                           │ :8006     │
                                           │ cart_db   │
                                           └─────┬─────┘
                                                 │
                                        ┌────────▼──┐
                                        │ order-    │
                                        │ service   │
                                        │ :8007     │
                                        │ order_db  │
                                        └───────────┘
```

### Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **No shared databases** | Each service has its own isolated MySQL database |
| **REST-only communication** | Services talk to each other only through HTTP requests (`requests` library) |
| **Single entry point** | All traffic from the browser goes through the API Gateway |
| **Stateless auth** | JWT tokens (HS256, 24h expiry), SHA-256 hashed passwords |

---

## Directory Structure

```
bookstore-microservice/
│
├── api-gateway/                # Port 8000 — Entry point + Web UI
│   ├── gateway/                #   Django project settings, main urls.py, SERVICE_MAP
│   ├── proxy/                  #   Generic reverse proxy (forwards /api/* to services)
│   ├── web/                    #   Django template views (home, cart, orders, login...)
│   └── templates/web/          #   HTML templates (15 pages)
│
├── staff-service/              # Port 8001 — Staff accounts + inventory logs
│   └── staff/                  #   Models: Staff, InventoryLog
│
├── manager-service/            # Port 8002 — Manager accounts + dashboard
│   └── manager/                #   Models: Manager | calls book/order/customer services
│
├── customer-service/           # Port 8003 — Customer registration, login, addresses
│   └── customer/               #   Models: Customer, Address | calls cart-service
│
├── catalog-service/            # Port 8004 — Book metadata catalog
│   └── catalog/                #   Models: Category, Author, Publisher
│
├── book-service/               # Port 8005 — Books, inventory, ratings
│   └── books/                  #   Models: Book, BookStatus, BookInventory
│                               #   Calls catalog-service to enrich book details
│
├── cart-service/               # Port 8006 — Shopping carts
│   └── cart/                   #   Models: Cart, CartItem | calls book-service
│
├── order-service/              # Port 8007 — Orders (orchestrator)
│   └── orders/                 #   Models: Order, OrderItem
│                               #   Orchestrates: cart → book-stock → pay → ship
│
├── ship-service/               # Port 8008 — Shipping methods and shipments
│   └── shipping/               #   Models: ShippingMethod, Shipment
│
├── pay-service/                # Port 8009 — Payment methods and payments
│   └── payment/                #   Models: PaymentMethod, Payment
│
├── comment-rate-service/       # Port 8010 — Reviews and ratings
│   └── comments/               #   Models: Review | calls book-service to update avg rating
│
├── recommender-ai-service/     # Port 8011 — Recommendations based on interactions
│   └── recommender/            #   Models: UserInteraction | SQL-based collaborative filtering
│
├── docker-compose.yml          # Run everything in Docker with one command
├── init.sql                    # Creates all 11 MySQL databases for Docker
├── run_local.py                # Start all 12 services locally (colored logs per service)
├── seed_data.py                # Insert sample data by calling REST APIs
├── setup_databases.py          # Drop/recreate all MySQL databases + run migrations
└── .env.example                # Template for environment variables
```

### What does each service own?

| Service | Database | Responsibility |
|---------|----------|----------------|
| api-gateway | SQLite (sessions only) | Route requests, serve web UI |
| staff-service | staff_db | Staff accounts, inventory audit logs |
| manager-service | manager_db | Manager accounts, business dashboard |
| customer-service | customer_db | Customer registration, login, addresses |
| catalog-service | catalog_db | Categories, authors, publishers |
| book-service | book_db | Books, stock levels, average ratings |
| cart-service | cart_db | Shopping carts and cart items |
| order-service | order_db | Orders, order items, order lifecycle |
| ship-service | ship_db | Shipping methods, shipment tracking |
| pay-service | pay_db | Payment methods, payment transactions |
| comment-rate-service | comment_db | Customer reviews and star ratings |
| recommender-ai-service | recommender_db | User interactions, recommendations |

---

## Prerequisites

### Required software

| Software | Version | Check |
|----------|---------|-------|
| Python | 3.10+ | `py --version` |
| MySQL | 8.0 | running on `localhost:3306` |
| pip | latest | `pip --version` |

### MySQL password

The project uses MySQL root password: **`paperrose`**

### Python packages (install once)

```bash
pip install django djangorestframework djangorestframework-simplejwt \
            PyJWT mysqlclient python-dotenv requests colorama corsheaders
```

Or install per-service:

```bash
# From bookstore-microservice/, install requirements for all services
for svc in staff-service manager-service customer-service catalog-service \
           book-service cart-service order-service ship-service pay-service \
           comment-rate-service recommender-ai-service api-gateway; do
    pip install -r $svc/requirements.txt 2>/dev/null || true
done
```

---

## Quick Start (3 Steps)

> Run these commands from inside the `bookstore-microservice/` directory.

### Step 1 — Set up databases

```bash
py setup_databases.py
```

This will:
- Drop and recreate all 11 MySQL databases
- Run `makemigrations` + `migrate` for every service
- Confirm: `11/11 OK`

### Step 2 — Start all services

```bash
py run_local.py
```

This starts 12 Django servers simultaneously (each in its own thread). Logs are color-coded per service. Leave this terminal running.

### Step 3 — Insert sample data

Open a **second terminal** in the same directory:

```bash
py seed_data.py
```

This calls each service's REST API to create sample staff, managers, customers, books, carts, orders, reviews, etc.

**Done.** Open your browser at **http://localhost:8000**

---

## Running Locally — Step by Step

### 1. Clone / open the project

```
cd bookstore-microservice/
```

### 2. Verify MySQL is running

```bash
"C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe" -u root -ppaperrose -e "SELECT 1;"
```

Expected output: `1`

### 3. Create and migrate databases

```bash
py setup_databases.py
# When prompted: type  y  and press Enter
```

Expected summary at the end:
```
=======================================================
  Migration Summary
=======================================================
  staff-service                  OK
  manager-service                OK
  customer-service               OK
  catalog-service                OK
  book-service                   OK
  cart-service                   OK
  order-service                  OK
  ship-service                   OK
  pay-service                    OK
  comment-rate-service           OK
  recommender-ai-service         OK
=======================================================
```

### 4. Migrate the API Gateway (SQLite)

```bash
cd api-gateway
py manage.py migrate
cd ..
```

### 5. Start all services

```bash
py run_local.py
```

Services and their ports:

| Color in terminal | Service | Port |
|-------------------|---------|------|
| Cyan | staff-service | 8001 |
| Magenta | manager-service | 8002 |
| Yellow | customer-service | 8003 |
| Green | catalog-service | 8004 |
| Blue | book-service | 8005 |
| White | cart-service | 8006 |
| Red | order-service | 8007 |
| Cyan (dim) | ship-service | 8008 |
| Green (dim) | pay-service | 8009 |
| Yellow (dim) | comment-rate-service | 8010 |
| Magenta (dim) | recommender-ai-service | 8011 |
| Bold White | api-gateway | 8000 |

### 6. Seed sample data

In a second terminal:

```bash
py seed_data.py
```

### 7. Open the web app

```
http://localhost:8000
```

---

## Running with Docker Compose

> Requires Docker Desktop installed and running.

```bash
# From bookstore-microservice/
docker compose up --build
```

This starts:
- One MySQL 8.0 container (`db`)
- 12 service containers (they wait for MySQL to be healthy before starting)

First run takes ~2-3 minutes to build. Once all containers are up:

```bash
# Seed sample data (from host, while containers are running)
py seed_data.py
```

Access the web UI: **http://localhost:8000**

To stop everything:

```bash
docker compose down
```

To stop and wipe all data:

```bash
docker compose down -v
```

---

## Sample Accounts

After running `seed_data.py`, the following accounts are available:

### Customers (login at http://localhost:8000/login/)

| Name | Email | Password |
|------|-------|----------|
| Alice Johnson | alice@example.com | `Customer123!` |
| Bob Williams | bob@example.com | `Customer123!` |
| Charlie Brown | charlie@example.com | `Customer123!` |
| Diana Prince | diana@example.com | `Customer123!` |
| Eve Thompson | eve@example.com | `Customer123!` |

### Staff (login at http://localhost:8000/staff/login/)

| Username | Password | Role |
|----------|----------|------|
| admin_staff | `Admin123!` | admin |
| inventory_john | `Staff123!` | staff |
| inventory_jane | `Staff123!` | staff |

### Managers (login at http://localhost:8000/manager/login/)

| Username | Password |
|----------|----------|
| super_manager | `Manager123!` |
| ops_manager | `Manager123!` |

---

## API Reference

All API endpoints are accessible at two levels:
- **Direct**: `http://localhost:{service_port}/api/{endpoint}/`
- **Via Gateway**: `http://localhost:8000/api/{endpoint}/`

### Staff Service — :8001

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/staff/login/` | Staff login → JWT token |
| GET | `/api/staff/` | List all staff |
| POST | `/api/staff/` | Create new staff account |
| GET | `/api/staff/{id}/` | Get staff by ID |
| PUT | `/api/staff/{id}/` | Update staff |
| DELETE | `/api/staff/{id}/` | Deactivate staff |
| GET | `/api/inventory-logs/` | List inventory logs |
| POST | `/api/inventory-logs/` | Create inventory log |

### Manager Service — :8002

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/managers/login/` | Manager login → JWT token |
| GET | `/api/managers/` | List all managers |
| POST | `/api/managers/` | Create manager account |
| GET | `/api/managers/{id}/` | Get manager by ID |
| GET | `/api/managers/dashboard/` | Dashboard stats (total books/orders/customers) |

### Customer Service — :8003

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/customers/register/` | Register new customer |
| POST | `/api/customers/login/` | Customer login → JWT token |
| GET | `/api/customers/{id}/` | Get customer profile |
| GET | `/api/customers/addresses/` | List addresses |
| POST | `/api/customers/addresses/` | Add address |

### Catalog Service — :8004

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List categories |
| POST | `/api/categories/` | Create category |
| GET | `/api/authors/` | List authors |
| POST | `/api/authors/` | Create author |
| GET | `/api/publishers/` | List publishers |
| POST | `/api/publishers/` | Create publisher |

### Book Service — :8005

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | List books (with filters) |
| POST | `/api/books/` | Create book |
| GET | `/api/books/{id}/` | Get book details |
| GET | `/api/books/{id}/full_details/` | Get book + category/author/publisher info |
| POST | `/api/books/{id}/add_stock/` | Add stock `{"quantity": N}` |
| POST | `/api/books/{id}/reduce_stock/` | Reduce stock `{"quantity": N}` |
| POST | `/api/books/bulk_check/` | Check stock for multiple books |
| GET | `/api/statuses/` | List book statuses |

### Cart Service — :8006

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/carts/{id}/` | Get cart details |
| GET | `/api/carts/active-cart/?customer_id={id}` | Get customer's active cart |
| POST | `/api/carts/create-for-customer/` | Create cart for new customer |
| POST | `/api/cart-items/` | Add item to cart |
| PUT | `/api/cart-items/{id}/` | Update quantity |
| DELETE | `/api/cart-items/{id}/` | Remove item from cart |
| POST | `/api/carts/{id}/clear/` | Clear all items |
| POST | `/api/carts/{id}/deactivate/` | Deactivate cart (after checkout) |

### Order Service — :8007

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/` | List all orders |
| POST | `/api/orders/` | Place order (orchestrates cart→stock→pay→ship) |
| GET | `/api/orders/{id}/` | Get order details |
| POST | `/api/orders/{id}/cancel/` | Cancel order |
| GET | `/api/orders/by-customer/{customer_id}/` | Customer's order history |
| GET | `/api/orders/by-number/{order_number}/` | Get by order number (UUID) |

### Ship Service — :8008

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/shipping-methods/` | List shipping options |
| GET | `/api/shipments/` | List shipments |
| GET | `/api/shipments/{id}/` | Get shipment details |
| POST | `/api/shipments/{id}/update_status/` | Update shipment status |

### Pay Service — :8009

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payment-methods/` | List payment methods |
| GET | `/api/payments/` | List payments |
| GET | `/api/payments/{id}/` | Get payment details |
| POST | `/api/payments/{id}/process/` | Mark payment as completed |
| POST | `/api/payments/{id}/refund/` | Refund a payment |

### Comment & Rate Service — :8010

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews/` | List reviews (filter: `?book_id=N`) |
| POST | `/api/reviews/` | Write a review |
| GET | `/api/reviews/{id}/` | Get review details |
| PUT | `/api/reviews/{id}/` | Update review |
| DELETE | `/api/reviews/{id}/` | Delete review |
| GET | `/api/reviews/stats/?book_id={id}` | Rating distribution for a book |

### Recommender AI Service — :8011

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interactions/` | Log a user interaction |
| GET | `/api/recommendations/?customer_id={id}` | Personalized recommendations |
| GET | `/api/trending/` | Trending books (last 30 days) |
| GET | `/api/best-rated/` | Top-rated books |
| GET | `/api/similar/?book_id={id}` | Similar books (by category) |

---

## Workflow Walkthroughs

### Customer Journey: Browse → Cart → Order

```
1. Register a new account
   POST /api/customers/register/
   Body: {"name": "John", "email": "john@example.com", "password": "Pass123!"}
   → Returns: customer_id, token

2. Browse books
   GET /api/books/
   → Returns: list of books with prices and stock

3. Get full book details (includes author, category, publisher)
   GET /api/books/1/full_details/

4. Add to cart
   POST /api/cart-items/
   Body: {"cart_id": {your_cart_id}, "book_id": 1, "quantity": 2}

5. View cart
   GET /api/carts/active-cart/?customer_id={your_id}

6. Place order
   POST /api/orders/
   Body: {
     "customer_id": 1,
     "cart_id": 1,
     "shipping_method_id": 1,
     "payment_method_id": 1,
     "shipping_address": "123 Main St"
   }
   → The order service automatically:
      - Reduces book stock
      - Deactivates the cart
      - Creates a payment record
      - Creates a shipment record
   → Returns: order details with order_number (UUID)

7. Track order
   GET /api/orders/by-number/{order_number}/
```

### Writing a Review

```
POST /api/reviews/
Body: {
  "customer_id": 1,
  "book_id": 1,
  "rating": 5,
  "title": "Great book!",
  "body": "Highly recommended."
}
→ Automatically updates the book's average rating in book-service
```

### Staff Inventory Management

```
1. Staff login
   POST /api/staff/login/
   Body: {"username": "admin_staff", "password": "Admin123!"}
   → Returns: token

2. Add stock to a book
   POST /api/books/1/add_stock/
   Body: {"quantity": 50, "reason": "Restocked from supplier"}

3. Check inventory log
   GET /api/inventory-logs/
```

### Manager Dashboard

```
1. Manager login
   POST /api/managers/login/
   Body: {"username": "super_manager", "password": "Manager123!"}
   → Returns: token (use as Bearer token in headers)

2. View dashboard (calls book, order, customer services internally)
   GET /api/managers/dashboard/
   Authorization: Bearer {token}
   → Returns: {"total_books": 10, "total_orders": 2, "total_customers": 5}
```

### Get Recommendations

```
1. Log that a customer viewed a book
   POST /api/interactions/
   Body: {"customer_id": 1, "book_id": 3, "interaction_type": "view"}

2. Get personalized recommendations
   GET /api/recommendations/?customer_id=1

3. Get trending books
   GET /api/trending/

4. Get similar books (same category)
   GET /api/similar/?book_id=1
```

---

## Service Communication Map

When a request arrives, here is how services call each other:

```
customer-service
  └─→ cart-service          (on register: create-for-customer)

book-service
  └─→ catalog-service       (on full_details: enrich with author/category/publisher)

cart-service
  └─→ book-service          (on add item: validate book exists and is in stock)

order-service               (on POST /api/orders/ — the main orchestrator)
  ├─→ cart-service          (get cart items)
  ├─→ book-service          (reduce stock for each item)
  ├─→ cart-service          (deactivate cart after order)
  ├─→ pay-service           (create payment record)
  └─→ ship-service          (create shipment record)

manager-service
  ├─→ book-service          (dashboard: total_books count)
  ├─→ order-service         (dashboard: total_orders count)
  └─→ customer-service      (dashboard: total_customers count)

comment-rate-service
  └─→ book-service          (after review create/update/delete: update avg_rating)
```

---

## Troubleshooting

### "Connection refused" when running seed_data.py

All services must be running first. Start them with:
```bash
py run_local.py
```
Wait until you see all ports listening, then run `seed_data.py` in a second terminal.

### MySQL authentication errors

Check that MySQL is running and the password is correct:
```bash
"C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe" -u root -ppaperrose -e "SHOW DATABASES;"
```

### "Table already exists" migration error

Run the setup script to clean-recreate all databases:
```bash
py setup_databases.py
```

### UnicodeEncodeError on Windows terminal

The scripts handle this automatically with `sys.stdout.reconfigure(encoding='utf-8')`. If you still see issues, run in a terminal that supports UTF-8 (Windows Terminal, VS Code integrated terminal).

### A service fails to start (port already in use)

Find and kill the process using the port:
```bash
netstat -ano | findstr :8001   # Replace 8001 with the conflicting port
taskkill /PID {PID} /F
```

### Django check fails for a service

Run the check manually to see detailed errors:
```bash
cd book-service
set DB_NAME=book_db
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=paperrose
py manage.py check
```

---

## Environment Variables

Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | MySQL host |
| `DB_USER` | root | MySQL user |
| `DB_PASSWORD` | paperrose | MySQL password |
| `DB_PORT` | 3306 | MySQL port |
| `STAFF_JWT_SECRET` | staff-jwt-secret | JWT signing key for staff tokens |
| `MANAGER_JWT_SECRET` | manager-jwt-secret | JWT signing key for manager tokens |
| `CUSTOMER_JWT_SECRET` | customer-jwt-secret | JWT signing key for customer tokens |

> In production, always override all JWT secrets with long random strings.
