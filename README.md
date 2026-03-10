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

## 🎯 Mục tiêu học tập

Dự án này giúp bạn **hiểu rõ sự khác biệt** giữa 3 kiểu kiến trúc phần mềm thông qua việc xây dựng **cùng một ứng dụng** (Book Store) theo 3 cách khác nhau.

---

## 📚 Giải thích 3 Kiến trúc

### 🏢 Version A: Monolithic Architecture (`/monolith`)

**Ý tưởng:** Tất cả trong một - giống như một ngôi nhà lớn chứa tất cả phòng.

```
┌─────────────────────────────────────────────────────┐
│                  MONOLITHIC APP                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ Accounts  │  │   Books   │  │   Cart    │       │
│  │  (login)  │◄─┤ (catalog) │◄─┤ (giỏ hàng)│       │
│  └───────────┘  └───────────┘  └───────────┘       │
│                       │                             │
│              ┌────────▼────────┐                    │
│              │   MySQL Database │                   │
│              │  (1 database)    │                   │
│              └──────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

**Đặc điểm:**
- ✅ **Đơn giản**: Dễ phát triển, dễ deploy (chỉ 1 app)
- ✅ **Dễ debug**: Tất cả code ở cùng một chỗ
- ❌ **Khó scale**: Phải scale cả hệ thống dù chỉ 1 phần bận
- ❌ **Rủi ro cao**: Lỗi 1 phần có thể làm sập cả hệ thống

**Phù hợp với:** Dự án nhỏ, MVP, startup giai đoạn đầu

---

### 🧅 Version B: Clean Architecture (`/clean`)

**Ý tưởng:** Tách biệt theo lớp (layers) - giống như củ hành, lớp trong không biết lớp ngoài.

```
┌─────────────────────────────────────────────────────────────┐
│  FRAMEWORK LAYER (Django views, templates, forms)           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  INFRASTRUCTURE LAYER (Django ORM repositories)       │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  INTERFACE LAYER (Repository interfaces)        │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  USE CASES LAYER (Business logic)         │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  DOMAIN LAYER (Entities: Customer,  │  │  │  │  │
│  │  │  │  │  Book, Cart - không phụ thuộc gì)   │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Nguyên tắc quan trọng:** Dependencies chỉ hướng VÀO TRONG
- Domain không biết gì về Use Cases
- Use Cases không biết gì về Infrastructure  
- Có thể thay Django bằng Flask mà không sửa Domain/Use Cases

**Đặc điểm:**
- ✅ **Dễ test**: Business logic tách biệt, test không cần database
- ✅ **Dễ bảo trì**: Thay đổi 1 layer không ảnh hưởng layer khác
- ✅ **Linh hoạt**: Dễ thay đổi framework, database
- ❌ **Phức tạp hơn**: Nhiều file, nhiều layer hơn Monolithic

**Phù hợp với:** Dự án trung bình-lớn, cần bảo trì lâu dài

---

### 🔌 Version C: Microservices Architecture (`/micro`)

**Ý tưởng:** Chia nhỏ thành các service độc lập - giống như nhiều ngôi nhà nhỏ, mỗi nhà làm 1 việc.

```
                    ┌─────────────────┐
                    │  Gateway (8000) │
                    │   (Web UI)      │
                    └────────┬────────┘
                             │ HTTP/REST
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Customer Service│ │  Book Service   │ │  Cart Service   │
│   (Port 8001)   │ │  (Port 8002)    │ │  (Port 8003)    │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ - Register      │ │ - List books    │ │ - Add to cart   │
│ - Login         │ │ - Book detail   │ │ - View cart     │
│ - Profile       │ │ - Search        │ │ - Update qty    │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ MySQL DB │        │ MySQL DB │        │ MySQL DB │
   │customers │        │  books   │        │  carts   │
   └──────────┘        └──────────┘        └──────────┘
```

**Đặc điểm:**
- ✅ **Scale độc lập**: Book Service bận? Chỉ scale Book Service
- ✅ **Công nghệ đa dạng**: Mỗi service có thể dùng ngôn ngữ/DB khác
- ✅ **Fault isolation**: 1 service chết, các service khác vẫn chạy
- ❌ **Phức tạp**: Cần xử lý network, distributed transactions
- ❌ **Khó debug**: Log nằm rải rác nhiều nơi

**Phù hợp với:** Dự án lớn, team lớn, cần scale cao

---

## 📊 So sánh 3 Kiến trúc

| Tiêu chí | 🏢 Monolithic | 🧅 Clean | 🔌 Microservices |
|----------|--------------|----------|------------------|
| **Độ phức tạp** | ⭐ Thấp | ⭐⭐ Trung bình | ⭐⭐⭐ Cao |
| **Số lượng deploy** | 1 app | 1 app | 4 services |
| **Database** | 1 DB chung | 1 DB chung | 3 DB riêng |
| **Coupling** | Cao (tight) | Thấp (loose) | Rất thấp |
| **Khả năng scale** | Scale cả app | Scale cả app | Scale từng service |
| **Khả năng test** | Khó | Dễ | Dễ nhất |
| **Khi nào dùng?** | MVP, startup | Dự án cần maintain | Dự án lớn, team lớn |

---

## 🔄 Luồng hoạt động "Thêm sách vào giỏ hàng"

### Monolithic:
```
User → View → Model.save() → Database → Response
(Tất cả trong 1 process)
```

### Clean Architecture:
```
User → View → UseCase.execute() → Repository.save() → Database → Response
(Tách biệt logic, nhưng vẫn 1 process)
```

### Microservices:
```
User → Gateway → HTTP Request → Cart Service → Database → Response
(Qua network, khác process)
```

---

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
