# Book Store Web System - Assignment 01

This project implements a Book Store Web System using Django + MySQL following three different architectural styles:

1. **Monolithic Architecture** (`/monolith`)
2. **Clean Architecture** (`/clean`)
3. **Microservices Architecture** (`/micro`)

## Project Structure

```
assignment_01/
├── monolith/                 # Version A - Monolithic Django
│   ├── bookstore/           # Main Django project
│   ├── accounts/            # Customer authentication app
│   ├── books/               # Book catalog app
│   ├── cart/                # Shopping cart app
│   ├── templates/           # HTML templates
│   └── sql/                 # Database initialization scripts
│
├── clean/                    # Version B - Clean Architecture
│   ├── domain/              # Enterprise business rules (entities)
│   ├── usecases/            # Application business rules
│   ├── interfaces/          # Interface adapters (repositories)
│   ├── infrastructure/      # Frameworks and drivers (DB implementations)
│   ├── framework/           # Django framework layer
│   └── sql/                 # Database initialization scripts
│
└── micro/                    # Version C - Microservices
    ├── customer-service/    # Customer management service (Port 8001)
    ├── book-service/        # Book catalog service (Port 8002)
    ├── cart-service/        # Shopping cart service (Port 8003)
    └── sql/                 # Database initialization scripts
```

## Entities

- **Customer**: id, name, email, password
- **Book**: id, title, author, price, stock
- **Cart**: id, customer_id, created_at
- **CartItem**: id, cart_id, book_id, quantity

## Functional Requirements

- ✅ Customer registration and login
- ✅ View book catalog
- ✅ Add books to shopping cart
- ✅ View shopping cart contents

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- pip (Python package manager)

## Quick Start

### 1. Install MySQL and create databases

```bash
# Run the SQL scripts for each version
mysql -u root -p < monolith/sql/init_database.sql
mysql -u root -p < clean/sql/init_database.sql
mysql -u root -p < micro/sql/init_databases.sql
```

### 2. Configure database passwords

Update the `DATABASES['default']['PASSWORD']` in the settings.py files:
- `monolith/bookstore/settings.py`
- `clean/framework/settings.py`
- `micro/customer-service/customer_service/settings.py`
- `micro/book-service/book_service/settings.py`
- `micro/cart-service/cart_service/settings.py`

### 3. Run each version

See individual README files in each directory for detailed instructions.

## Architecture Comparison

| Feature | Monolithic | Clean Architecture | Microservices |
|---------|------------|-------------------|---------------|
| Deployment | Single unit | Single unit | Multiple services |
| Database | Single DB | Single DB | Multiple DBs |
| Coupling | High | Low | Very Low |
| Complexity | Low | Medium | High |
| Scalability | Limited | Medium | High |
| Testing | Harder | Easier | Easiest |

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: MySQL 8.0+
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5 + HTML Templates

## Author

PTIT Student - Assignment 01

## License

This project is for educational purposes only.
