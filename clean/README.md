# Clean Architecture Django - Book Store

This is the **Clean Architecture** version of the Book Store Web System.

## Architecture Overview

```
clean/
├── domain/                  # LAYER 1: Enterprise Business Rules
│   └── entities/           # Business entities (independent of frameworks)
│       ├── customer.py     # Customer entity
│       ├── book.py         # Book entity
│       └── cart.py         # Cart, CartItem entities
│
├── usecases/               # LAYER 2: Application Business Rules
│   ├── customer_usecases.py  # Register, Login, Get customer
│   ├── book_usecases.py      # Get books, Search, CRUD
│   └── cart_usecases.py      # Add to cart, Update, Remove, Clear
│
├── interfaces/             # LAYER 3: Interface Adapters
│   └── repositories/       # Repository interfaces (contracts)
│       ├── customer_repository.py
│       ├── book_repository.py
│       └── cart_repository.py
│
├── infrastructure/         # LAYER 4: Frameworks & Drivers
│   └── repositories/       # Repository implementations
│       ├── django_customer_repository.py
│       ├── django_book_repository.py
│       └── django_cart_repository.py
│
├── framework/              # Django Framework Integration
│   ├── settings.py
│   ├── urls.py
│   ├── models.py          # Django ORM models
│   ├── views.py           # Controllers/Presenters
│   ├── forms.py
│   └── templates/         # HTML templates
│
└── sql/                    # Database scripts
```

## Clean Architecture Principles

1. **Independence of Frameworks**: The business logic doesn't depend on Django
2. **Testability**: Business rules can be tested without UI, database, or external services
3. **Independence of UI**: The UI can change without affecting business rules
4. **Independence of Database**: Business rules are not bound to MySQL
5. **Independence of External Agency**: Business rules don't know about outside world

## Dependency Rule

Dependencies only point inward:
```
Framework → Infrastructure → Interfaces → Use Cases → Domain
```

## Setup Instructions

### 1. Create virtual environment

```bash
cd clean
py -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create MySQL database

```bash
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u root -p < sql/init_database.sql
```

Or manually:
```sql
CREATE DATABASE bookstore_clean CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Update database settings

Edit `framework/settings.py` and update the MySQL password:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore_clean',
        'USER': 'root',
        'PASSWORD': 'your_password_here',  # Update this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Run migrations

```bash
py manage.py migrate
```

### 6. Create superuser (optional)

```bash
py manage.py createsuperuser
```

### 7. Run the server

```bash
py manage.py runserver
```

Visit: http://localhost:8000

## URLs

- **Home**: http://localhost:8000/
- **Book Catalog**: http://localhost:8000/books/
- **Login**: http://localhost:8000/accounts/login/
- **Register**: http://localhost:8000/accounts/register/
- **Cart**: http://localhost:8000/cart/
- **Admin**: http://localhost:8000/admin/

## Key Differences from Monolithic

| Aspect | Monolithic | Clean Architecture |
|--------|------------|-------------------|
| Business Logic | In Django models/views | In domain entities & use cases |
| Data Access | Direct ORM queries | Through repository interfaces |
| Dependencies | Django everywhere | Django only in outer layers |
| Testing | Requires Django | Core logic testable in isolation |
| Flexibility | Harder to change DB | Easy to swap implementations |

## Example: How a Request Flows

1. **HTTP Request** → Django URL router
2. **View** (framework) → Calls Use Case
3. **Use Case** (usecases) → Contains business logic, calls Repository Interface
4. **Repository Interface** (interfaces) → Abstract contract
5. **Repository Implementation** (infrastructure) → Django ORM queries
6. **Database** → MySQL

## Project Characteristics

- ✅ Framework-independent business logic
- ✅ Testable use cases
- ✅ Swappable infrastructure
- ✅ Clear separation of concerns
- ✅ Following SOLID principles
