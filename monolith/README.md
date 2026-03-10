# 📚 Hệ thống Quản lý Nhà sách Trực tuyến - Monolithic Architecture

## Mục lục
1. [Giới thiệu](#giới-thiệu)
2. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
3. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
4. [Cài đặt](#cài-đặt)
5. [Cấu hình](#cấu-hình)
6. [Chức năng hệ thống](#chức-năng-hệ-thống)
7. [Mô hình dữ liệu](#mô-hình-dữ-liệu)
8. [API Endpoints](#api-endpoints)
9. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)

---

## Giới thiệu

Hệ thống quản lý nhà sách trực tuyến được xây dựng theo **kiến trúc Monolithic** với Django Framework. Hệ thống hỗ trợ các chức năng:

### Đối với Nhân viên (Staff):
- ✅ Quản lý nhập kho sách
- ✅ Quản lý tồn kho
- ✅ Điều chỉnh số lượng sách
- ✅ Xem lịch sử nhập/xuất kho
- ✅ Dashboard tổng quan

### Đối với Khách hàng (Customer):
- ✅ Tìm kiếm và xem sách
- ✅ Lọc theo danh mục, tác giả, giá
- ✅ Tạo và quản lý giỏ hàng
- ✅ Đặt hàng và thanh toán
- ✅ Chọn phương thức thanh toán
- ✅ Chọn phương thức vận chuyển
- ✅ Theo dõi đơn hàng
- ✅ Đánh giá và nhận xét sách
- ✅ Nhận gợi ý sách (dựa trên lịch sử mua hàng và đánh giá)

---

## Kiến trúc hệ thống

### Monolithic Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BOOKSTORE MONOLITHIC APPLICATION                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      PRESENTATION LAYER                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│  │  │  Templates  │  │   Static    │  │      Forms          │  │   │
│  │  │   (HTML)    │  │  (CSS/JS)   │  │   (Validation)      │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      CONTROLLER LAYER                        │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │   │
│  │  │book_controller│ │cart_controller│ │  order_controller   │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘ │   │
│  │  ┌──────────────┐ ┌──────────────────────────────────────┐  │   │
│  │  │staff_controller│ │      customer_controller           │  │   │
│  │  └──────────────┘ └──────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        MODEL LAYER                           │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐ │   │
│  │  │   Book     │ │  Customer  │ │   Order    │ │   Staff   │ │   │
│  │  │  Domain    │ │   Domain   │ │   Domain   │ │  Domain   │ │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └───────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │              Review & Recommendation Domain            │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     DATABASE (MySQL)                         │   │
│  │                   bookstore_monolith                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Ưu điểm của Monolithic:
- ✅ **Đơn giản**: Dễ phát triển và hiểu
- ✅ **Dễ deploy**: Chỉ cần deploy một ứng dụng
- ✅ **Debug dễ dàng**: Tất cả code trong một project
- ✅ **Transaction đơn giản**: Sử dụng database transaction thông thường

### Nhược điểm:
- ❌ **Khó scale**: Phải scale toàn bộ ứng dụng
- ❌ **Single point of failure**: Một lỗi có thể ảnh hưởng toàn hệ thống
- ❌ **Team coupling**: Các team phải làm việc trên cùng codebase

---

## Cấu trúc thư mục

```
monolith/
├── bookstore/                    # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py               # Cấu hình Django (DB, Apps, etc.)
│   ├── urls.py                   # URL routing chính
│   ├── wsgi.py                   # WSGI entry point
│   └── asgi.py                   # ASGI entry point
│
├── store/                        # Main Application (MVC + Domain)
│   ├── __init__.py
│   ├── apps.py                   # App configuration
│   │
│   ├── models/                   # MODEL LAYER (Domain Entities)
│   │   ├── __init__.py           # Export all models
│   │   │
│   │   ├── book/                 # Book Domain
│   │   │   ├── __init__.py
│   │   │   └── book.py           # Book, Author, Category, Publisher,
│   │   │                         # BookImage, BookDescription, BookStatus,
│   │   │                         # BookTag, BookInventory, BookRating
│   │   │
│   │   ├── customer/             # Customer Domain
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # User, UserProfile, UserRole, UserStatus,
│   │   │   │                     # LoginSession
│   │   │   └── customer.py       # Customer (extends User)
│   │   │
│   │   ├── order/                # Order Domain
│   │   │   ├── __init__.py
│   │   │   ├── cart.py           # Cart, CartItem, CartStatus, SavedCart,
│   │   │   │                     # CartHistory, CartSummary
│   │   │   └── order.py          # Order, OrderItem, OrderStatus, OrderHistory,
│   │   │                         # OrderTracking, OrderCancellation, Invoice,
│   │   │                         # Payment, PaymentMethod, PaymentStatus,
│   │   │                         # Transaction, Refund,
│   │   │                         # Shipping, ShippingMethod, ShippingStatus,
│   │   │                         # DeliveryAddress, DeliveryTracking
│   │   │
│   │   ├── staff/                # Staff Domain
│   │   │   ├── __init__.py
│   │   │   └── staff.py          # Staff, Admin, InventoryLog, AdminActionLog
│   │   │
│   │   └── review/               # Review & Recommendation Domain
│   │       ├── __init__.py
│   │       └── review.py         # Rating, Review, UserBehavior,
│   │                             # PurchaseHistory, RecommendationRule,
│   │                             # Recommendation
│   │
│   ├── controllers/              # CONTROLLER LAYER (Views/Logic)
│   │   │
│   │   ├── bookController/
│   │   │   ├── __init__.py
│   │   │   └── book_controller.py    # Book catalog, search, filter,
│   │   │                             # categories, authors, recommendations
│   │   │
│   │   ├── orderController/
│   │   │   ├── __init__.py
│   │   │   ├── cart_controller.py    # Cart CRUD, save/restore cart
│   │   │   └── order_controller.py   # Checkout, payment, shipping,
│   │   │                             # tracking, rating, review
│   │   │
│   │   ├── customerController/
│   │   │   ├── __init__.py
│   │   │   └── customer_controller.py # Auth, profile, address
│   │   │
│   │   └── staffController/
│   │       ├── __init__.py
│   │       └── staff_controller.py   # Staff login, dashboard,
│   │                                 # inventory management
│   │
│   ├── urls/                     # URL ROUTING (Per domain)
│   │   ├── __init__.py
│   │   ├── book_urls.py
│   │   ├── order_urls.py
│   │   ├── customer_urls.py
│   │   └── staff_urls.py
│   │
│   └── templates/                # VIEW LAYER (HTML Templates)
│       ├── base.html             # Base template
│       ├── books/                # Book templates
│       │   ├── list.html
│       │   ├── detail.html
│       │   ├── categories.html
│       │   ├── category_detail.html
│       │   ├── authors.html
│       │   └── author_detail.html
│       ├── cart/                 # Cart templates
│       │   ├── cart.html
│       │   └── saved_carts.html
│       ├── order/                # Order templates
│       │   ├── checkout.html
│       │   ├── orders.html
│       │   ├── order_detail.html
│       │   ├── track_order.html
│       │   ├── rate_book.html
│       │   ├── write_review.html
│       │   ├── address_list.html
│       │   └── add_address.html
│       ├── accounts/             # Customer account templates
│       │   ├── login.html
│       │   ├── register.html
│       │   └── profile.html
│       └── staff/                # Staff admin templates
│           ├── base_staff.html
│           ├── login.html
│           ├── dashboard.html
│           ├── inventory_list.html
│           ├── add_book.html
│           ├── import_stock.html
│           └── inventory_logs.html
│
├── static/                       # Static files (CSS, JS, Images)
│
├── sql/
│   └── init_database.sql         # Database initialization script
│
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── README.md                     # This documentation
```

---

## Cài đặt

### Yêu cầu hệ thống
- Python 3.10+
- MySQL 8.0+
- pip (Python package manager)

### Bước 1: Clone và cài đặt dependencies

```bash
# Di chuyển đến thư mục project
cd monolith

# Tạo virtual environment (khuyến nghị)
py -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 2: Cấu hình Database

1. Tạo database MySQL:
```sql
CREATE DATABASE bookstore_monolith CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Chạy script khởi tạo (tùy chọn - để có dữ liệu mẫu):
```bash
mysql -u root -p bookstore_monolith < sql/init_database.sql
```

3. Hoặc sử dụng Django migrations:
```bash
py manage.py makemigrations
py manage.py migrate
```

### Bước 3: Tạo superuser (Admin)

```bash
py manage.py createsuperuser
```

### Bước 4: Chạy server

```bash
py manage.py runserver
```

Truy cập: http://127.0.0.1:8000

---

## Cấu hình

### Database Configuration (settings.py)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore_monolith',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}
```

### Custom User Model

```python
AUTH_USER_MODEL = 'store.Customer'
```

---

## Chức năng hệ thống

### 1. Quản lý Sách (Book Management)

#### Xem danh sách sách
- URL: `/books/`
- Hỗ trợ: Tìm kiếm, lọc theo danh mục/tác giả/giá, sắp xếp, phân trang

#### Xem chi tiết sách
- URL: `/books/<id>/`
- Hiển thị: Thông tin đầy đủ, đánh giá, sách liên quan, gợi ý

#### Danh mục
- URL: `/books/categories/`
- URL: `/books/categories/<id>/`

#### Tác giả
- URL: `/books/authors/`
- URL: `/books/authors/<id>/`

### 2. Giỏ hàng (Cart)

#### Xem giỏ hàng
- URL: `/cart/`

#### Thao tác giỏ hàng
- Thêm sách: `POST /cart/add/<book_id>/`
- Cập nhật số lượng: `POST /cart/update/<item_id>/`
- Xóa item: `POST /cart/remove/<item_id>/`
- Xóa toàn bộ: `POST /cart/clear/`

#### Lưu giỏ hàng
- Lưu: `POST /cart/save/`
- Xem danh sách đã lưu: `/cart/saved/`
- Khôi phục: `POST /cart/restore/<saved_id>/`

### 3. Đặt hàng (Order)

#### Checkout
- URL: `/cart/checkout/`
- Chọn địa chỉ giao hàng
- Chọn phương thức vận chuyển
- Chọn phương thức thanh toán

#### Xem đơn hàng
- Danh sách: `/cart/orders/`
- Chi tiết: `/cart/orders/<id>/`
- Theo dõi: `/cart/orders/<id>/track/`

#### Hủy đơn hàng
- URL: `POST /cart/orders/<id>/cancel/`

### 4. Thanh toán (Payment)

#### Phương thức thanh toán hỗ trợ:
- COD (Tiền mặt khi nhận hàng)
- Chuyển khoản ngân hàng
- Ví MoMo
- Ví ZaloPay
- VNPay
- Thẻ tín dụng/ghi nợ

### 5. Vận chuyển (Shipping)

#### Phương thức vận chuyển:
- Giao hàng tiêu chuẩn (3-5 ngày) - 25,000đ
- Giao hàng nhanh (1-2 ngày) - 45,000đ
- Giao hàng hỏa tốc (trong ngày) - 65,000đ
- Miễn phí (đơn từ 500k, 3-7 ngày)

### 6. Đánh giá & Nhận xét (Review)

#### Đánh giá sách
- URL: `/cart/orders/<order_id>/rate/<book_id>/`
- Điểm: 1-5 sao

#### Viết nhận xét
- URL: `/cart/review/<book_id>/`
- Tiêu đề, nội dung, ưu/nhược điểm

### 7. Gợi ý sách (Recommendation)

#### Thuật toán gợi ý dựa trên:
- **Lịch sử mua hàng**: Sách cùng tác giả/danh mục với sách đã mua
- **Đánh giá cao**: Sách có điểm đánh giá cao
- **Collaborative filtering**: Sách mà khách hàng tương tự đã mua
- **Sách bán chạy**: Top sách bán chạy

### 8. Quản lý Nhân viên (Staff)

#### Đăng nhập
- URL: `/staff/login/`

#### Dashboard
- URL: `/staff/dashboard/`
- Thống kê: Tổng sách, sách sắp hết, đơn chờ xử lý, khách hàng

#### Quản lý tồn kho
- Danh sách: `/staff/inventory/`
- Thêm sách: `/staff/inventory/add/`
- Nhập kho: `/staff/inventory/import/`
- Nhập hàng loạt: `/staff/inventory/bulk-import/`
- Điều chỉnh: `/staff/inventory/adjust/`
- Lịch sử: `/staff/inventory/logs/`

---

## Mô hình dữ liệu

### Class Diagram (Tổng quan)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          BOOK DOMAIN                                │
├─────────────────────────────────────────────────────────────────────┤
│  Book ◄── BookImage, BookDescription, BookInventory, BookTag       │
│    ├── author_id ──► Author                                        │
│    ├── category_id ──► Category (self-referencing for parent)      │
│    ├── publisher_id ──► Publisher                                  │
│    └── status_id ──► BookStatus                                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        CUSTOMER DOMAIN                              │
├─────────────────────────────────────────────────────────────────────┤
│  Customer (extends AbstractBaseUser)                                │
│    ├── UserProfile (1:1)                                           │
│    ├── LoginSession (1:N)                                          │
│    ├── Cart (1:N)                                                  │
│    ├── Order (1:N)                                                 │
│    └── DeliveryAddress (1:N)                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         ORDER DOMAIN                                │
├─────────────────────────────────────────────────────────────────────┤
│  Cart ◄── CartItem ──► Book                                        │
│    ├── status_id ──► CartStatus                                    │
│    └── SavedCart, CartHistory                                      │
│                                                                     │
│  Order ◄── OrderItem ──► Book                                      │
│    ├── status_id ──► OrderStatus                                   │
│    ├── Payment ──► PaymentMethod, PaymentStatus                    │
│    ├── Shipping ──► ShippingMethod, ShippingStatus, DeliveryAddress│
│    └── OrderHistory, OrderTracking, OrderCancellation, Invoice     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     REVIEW & RECOMMENDATION                         │
├─────────────────────────────────────────────────────────────────────┤
│  Rating (Customer + Book) ◄── Review                               │
│  UserBehavior (Customer + Book) - tracking views, purchases        │
│  PurchaseHistory (Customer + Book)                                 │
│  Recommendation (Customer + Book) ◄── RecommendationRule           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         STAFF DOMAIN                                │
├─────────────────────────────────────────────────────────────────────┤
│  Staff ◄── Admin (1:1)                                             │
│  InventoryLog (Staff + Book) - track stock changes                 │
│  AdminActionLog (Admin) - track admin actions                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Các Model chính

| Model | Mô tả | Các trường chính |
|-------|-------|------------------|
| **Book** | Thông tin sách | isbn, title, author, category, price, stock_quantity, average_rating |
| **Author** | Tác giả | name, biography, nationality |
| **Category** | Danh mục | name, description, parent, icon |
| **Publisher** | Nhà xuất bản | name, address, contact_email |
| **Customer** | Khách hàng | name, email, phone, address, password |
| **Cart** | Giỏ hàng | customer, status, total_price |
| **CartItem** | Item trong giỏ | cart, book, quantity, unit_price |
| **Order** | Đơn hàng | order_number, customer, status, total_price, shipping_fee |
| **OrderItem** | Item trong đơn | order, book, quantity, unit_price, subtotal |
| **Payment** | Thanh toán | order, method, status, amount, transaction_id |
| **Shipping** | Vận chuyển | order, method, status, tracking_number, delivery_address |
| **Rating** | Đánh giá | book, customer, score (1-5) |
| **Review** | Nhận xét | rating, title, content, pros, cons |
| **Staff** | Nhân viên | name, email, password, role |
| **InventoryLog** | Lịch sử kho | book, staff, change_type, quantity_change |

---

## API Endpoints

### Book APIs

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/books/` | Danh sách sách |
| GET | `/api/books/<id>/` | Chi tiết sách |
| GET | `/api/categories/` | Danh sách danh mục |
| GET | `/api/authors/` | Danh sách tác giả |
| GET | `/api/recommendations/` | Gợi ý sách cho user |

### Cart APIs

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/cart/api/` | Giỏ hàng hiện tại |
| POST | `/cart/add/<book_id>/` | Thêm sách vào giỏ |
| POST | `/cart/update/<item_id>/` | Cập nhật số lượng |
| POST | `/cart/remove/<item_id>/` | Xóa item |

### Order APIs

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/cart/api/orders/` | Danh sách đơn hàng |
| GET | `/cart/api/shipping-methods/` | Phương thức vận chuyển |
| GET | `/cart/api/payment-methods/` | Phương thức thanh toán |

### Staff APIs

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/staff/api/inventory/` | Trạng thái tồn kho |
| POST | `/staff/api/quick-import/` | Nhập nhanh tồn kho |

---

## Hướng dẫn sử dụng

### Đối với Khách hàng

1. **Đăng ký/Đăng nhập**
   - Truy cập `/accounts/register/` để đăng ký
   - Truy cập `/accounts/login/` để đăng nhập

2. **Tìm kiếm sách**
   - Truy cập `/books/` để xem danh sách
   - Sử dụng ô tìm kiếm hoặc bộ lọc

3. **Mua hàng**
   - Click "Thêm vào giỏ" ở trang chi tiết sách
   - Truy cập giỏ hàng, kiểm tra và click "Thanh toán"
   - Chọn địa chỉ, phương thức vận chuyển và thanh toán
   - Xác nhận đơn hàng

4. **Theo dõi đơn hàng**
   - Truy cập `/cart/orders/` để xem danh sách đơn
   - Click vào đơn để xem chi tiết và theo dõi

### Đối với Nhân viên

1. **Đăng nhập**
   - Truy cập `/staff/login/`
   - Nhập thông tin đăng nhập

2. **Quản lý tồn kho**
   - Truy cập Dashboard để xem tổng quan
   - Vào "Tồn kho" để xem danh sách sách
   - Sử dụng "Nhập kho" để thêm số lượng
   - Sử dụng "Điều chỉnh" để sửa số lượng

3. **Thêm sách mới**
   - Click "Thêm sách mới" trong trang tồn kho
   - Điền thông tin và lưu

---

## Ghi chú phát triển

### Các công nghệ sử dụng
- **Backend**: Django 5.x
- **Database**: MySQL 8.0
- **Frontend**: Django Templates, HTML5, CSS3, JavaScript
- **Authentication**: Django built-in + Session-based (Staff)

### Các thư viện Python
```
Django>=5.0
mysqlclient>=2.2.0
Pillow>=10.0.0  # Image handling
```

### Mẫu thiết kế áp dụng
- **MVC Pattern**: Model-View-Controller (Django's MTV)
- **Repository Pattern**: Abstraction layer for data access
- **Factory Pattern**: Object creation
- **Domain-Driven Design**: Organize code by business domains

---

## License

MIT License

---

## Tác giả

Được phát triển như một dự án học tập về kiến trúc phần mềm.
