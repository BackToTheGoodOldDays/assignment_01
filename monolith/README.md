# Monolithic Django - Book Store

This is the **Monolithic Architecture** version of the Book Store Web System.

## Architecture Overview

```
monolith/
├── bookstore/           # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/            # Customer authentication app
│   ├── models.py       # Customer model
│   ├── views.py        # Login, Register, Profile views
│   └── forms.py        # Authentication forms
├── books/               # Book catalog app
│   ├── models.py       # Book model
│   └── views.py        # Catalog, Detail views
├── cart/                # Shopping cart app
│   ├── models.py       # Cart, CartItem models
│   └── views.py        # Cart management views
├── templates/           # HTML templates
└── sql/                 # Database scripts
```

## Setup Instructions

### 1. Create virtual environment

```bash
cd monolith
py -m venv venv

# Windows
venv\Scripts\activate

#Git Bash - cần đổi thành:
source venv/Scripts/activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create MySQL database

```bash
mysql -u root -p < sql/init_database.sql
```

Or manually:
```sql
CREATE DATABASE bookstore_monolith CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Update database settings

Edit `bookstore/settings.py` and update the MySQL password:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore_monolith',
        'USER': 'root',
        'PASSWORD': 'paperrose',  # Update this
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

### 7. Load sample data (optional)

```bash
py manage.py loaddata books
```

Or insert via SQL script.

### 8. Run the server

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

## Features

- ✅ Customer registration and login
- ✅ View book catalog with search
- ✅ View book details
- ✅ Add books to cart
- ✅ Update cart item quantities
- ✅ Remove items from cart
- ✅ Clear cart

## Project Characteristics

- **Single Django Project**: All functionality in one application
- **Shared Database**: All models use the same MySQL database
- **Tightly Coupled**: Apps can directly import from each other
- **Simple Deployment**: Single deployment unit
