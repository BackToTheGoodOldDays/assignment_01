# BÁO CÁO KỸ THUẬT

# Hệ thống quản lý nhà sách trực tuyến BookStore

## 1. Tổng quan dự án

### 1.1. Giới thiệu

Dự án xây dựng hệ thống nhà sách trực tuyến (Online Bookstore) theo **kiến trúc Microservices**, trong đó toàn bộ hệ thống được phân tách thành **12 dịch vụ độc lập**, mỗi dịch vụ đảm nhận một miền nghiệp vụ riêng biệt. Các dịch vụ giao tiếp với nhau thông qua **RESTful HTTP API**, mỗi dịch vụ sở hữu **database riêng** (Database per Service pattern), và có thể được triển khai, mở rộng (scale) cũng như cập nhật một cách độc lập.

Hệ thống hỗ trợ đầy đủ các chức năng thương mại điện tử cơ bản: quản lý khách hàng, duyệt và tìm kiếm sách, giỏ hàng, đặt hàng, thanh toán, vận chuyển, đánh giá sản phẩm, và gợi ý sách bằng trí tuệ nhân tạo (AI).

### 1.2. Yêu cầu chức năng

| STT | Nhóm chức năng | Mô tả |
|-----|---------------|-------|
| 1 | Quản lý khách hàng | Đăng ký, đăng nhập (JWT), quản lý profile, địa chỉ giao hàng |
| 2 | Danh mục sách | Quản lý danh mục, tác giả, nhà xuất bản (dữ liệu master) |
| 3 | Quản lý sách | CRUD sách, hình ảnh, mô tả chi tiết, quản lý tồn kho, đánh giá trung bình |
| 4 | Giỏ hàng | Thêm/sửa/xóa sản phẩm, lưu giỏ hàng, khôi phục giỏ đã lưu |
| 5 | Đơn hàng | Tạo đơn từ giỏ hàng, theo dõi trạng thái, hủy đơn |
| 6 | Thanh toán | Hỗ trợ COD, chuyển khoản, MoMo, VNPay; xử lý và xác nhận thanh toán |
| 7 | Vận chuyển | 3 phương thức (tiêu chuẩn/nhanh/hỏa tốc), theo dõi vận đơn |
| 8 | Đánh giá & bình luận | Đánh giá 1–5 sao, viết bình luận, phê duyệt bởi staff |
| 9 | Gợi ý sách (AI) | Gợi ý dựa trên lịch sử mua, sách trending, sách tương tự |
| 10 | Quản lý nhân viên | Đăng nhập staff, quản lý kho, ghi log nhập hàng |
| 11 | Quản lý cấp cao | Dashboard thống kê, báo cáo doanh thu và tồn kho |

### 1.3. Công nghệ sử dụng

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Backend Framework | Django + Django REST Framework | 4.2+ |
| Cơ sở dữ liệu | MySQL | 8.0+ |
| Ngôn ngữ lập trình | Python | 3.11 |
| Giao diện Web | Bootstrap 5, HTML5, CSS3, JavaScript | - |
| Template Engine | Django Template Language (DTL) | - |
| API Protocol | RESTful HTTP/JSON | - |
| Xác thực | JWT (JSON Web Token, HS256) | - |
| Containerization | Docker | - |
| Quản lý mã nguồn | Git, GitHub | - |
| Machine Learning | NumPy, scikit-learn (Recommender Service) | - |

### 1.4. Luồng nghiệp vụ chính

```
[Đăng ký] ──► Customer Service tạo tài khoản
     │
     ▼
[Tạo giỏ hàng] ──► Customer Service gọi HTTP POST đến Cart Service
     │
     ▼
[Duyệt sách] ──► API Gateway → Book Service (lấy danh sách, tìm kiếm)
     │                              │
     ▼                              ▼
[Thêm vào giỏ] ──► Cart Service gọi Book Service kiểm tra tồn kho
     │
     ▼
[Checkout] ──► Order Service tạo đơn hàng
     │           ├─► gọi Book Service (giảm tồn kho)
     │           ├─► gọi Cart Service (đóng giỏ hàng)
     │           ├─► gọi Pay Service (tạo thanh toán)
     │           └─► gọi Ship Service (tạo vận đơn)
     │
     ▼
[Thanh toán] ──► Pay Service xử lý, cập nhật trạng thái
     │
     ▼
[Giao hàng] ──► Ship Service cập nhật tracking
     │
     ▼
[Đánh giá] ──► Comment-Rate Service
                   └─► gọi Book Service cập nhật điểm trung bình
```

---

## 2. Kiến trúc hệ thống

### 2.1. Sơ đồ kiến trúc tổng quan

```
                         ┌─────────────────────────┐
                         │        Client            │
                         │  (Browser / Mobile App)  │
                         └────────────┬─────────────┘
                                      │ HTTP
                         ┌────────────▼─────────────┐
                         │      API Gateway          │
                         │     (Port 8000)           │
                         │  ┌─────────────────────┐  │
                         │  │ Session Management  │  │
                         │  │ JWT Verification    │  │
                         │  │ Request Routing     │  │
                         │  │ Web UI (SSR)        │  │
                         │  └─────────────────────┘  │
                         └────────────┬──────────────┘
                                      │ HTTP/REST (Internal)
         ┌──────────┬──────────┬──────┼──────┬──────────┬──────────┐
         │          │          │      │      │          │          │
         ▼          ▼          ▼      ▼      ▼          ▼          ▼
    ┌─────────┐┌─────────┐┌──────┐┌──────┐┌──────┐┌─────────┐┌─────────┐
    │Customer ││Catalog  ││ Book ││ Cart ││Order ││  Ship   ││  Pay    │
    │ Service ││Service  ││Serv. ││Serv. ││Serv. ││ Service ││Service  │
    │ :8003   ││ :8004   ││:8005 ││:8006 ││:8007 ││ :8008   ││ :8009   │
    └────┬────┘└────┬────┘└──┬───┘└──┬───┘└──┬───┘└────┬────┘└────┬────┘
         │          │        │       │       │         │          │
         ▼          ▼        ▼       ▼       ▼         ▼          ▼
    ┌─────────┐┌─────────┐┌──────┐┌──────┐┌──────┐┌─────────┐┌─────────┐
    │customer ││catalog  ││book  ││cart  ││order ││ ship    ││ pay     │
    │  _db    ││  _db    ││ _db  ││ _db  ││ _db  ││  _db    ││  _db    │
    └─────────┘└─────────┘└──────┘└──────┘└──────┘└─────────┘└─────────┘

    ┌──────────┬──────────┬──────────┬──────────┐
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌──────────┐┌──────────┐┌──────────┐
│  Staff  ││Manager  ││ Comment  ││Recomm.  ││ manager  │
│ Service ││Service  ││  Rate    ││   AI    ││   _db    │
│ :8001   ││ :8002   ││ :8010    ││ :8011   │└──────────┘
└────┬────┘└────┬────┘└────┬─────┘└────┬────┘
     ▼          ▼          ▼           ▼
┌─────────┐┌─────────┐┌──────────┐┌──────────┐
│staff_db ││manager  ││comment   ││recomm.   │
│         ││  _db    ││  _db     ││  _db     │
└─────────┘└─────────┘└──────────┘└──────────┘
```

### 2.2. Nguyên tắc thiết kế

Hệ thống tuân thủ các nguyên tắc cốt lõi của kiến trúc microservices:

**1. Single Responsibility Principle (SRP)**  
Mỗi dịch vụ chỉ đảm nhận một miền nghiệp vụ duy nhất. Ví dụ: Book Service chỉ xử lý sách, tồn kho và đánh giá; Cart Service chỉ xử lý giỏ hàng.

**2. Database per Service**  
Mỗi dịch vụ sở hữu database riêng (11 MySQL databases). Không có Foreign Key liên cơ sở dữ liệu. Các liên kết giữa services sử dụng IntegerField lưu ID tham chiếu và giao tiếp qua HTTP API.

**3. API-First Design**  
Mỗi service expose RESTful API chuẩn JSON. Sử dụng Django REST Framework với ViewSet, Serializer, Router pattern. Hỗ trợ filtering, searching, ordering, pagination.

**4. Loose Coupling**  
Các services chỉ biết nhau qua HTTP endpoint. Khi một service ngừng hoạt động, các service khác xử lý graceful degradation thay vì crash.

**5. Independent Deployment**  
Mỗi service có thể build, test, deploy riêng biệt. Mỗi service có `Dockerfile`, `requirements.txt`, `manage.py` và `settings.py` riêng.

### 2.3. Cấu trúc thư mục

```
micro/
├── api-gateway/              # Cổng API + Web UI (Port 8000)
│   ├── gateway/              # Django project settings
│   ├── api/                  # Proxy views, routing logic
│   └── templates/            # HTML templates (SSR)
│       ├── base.html
│       ├── accounts/         # Login, register, profile
│       ├── books/            # Catalog, detail
│       ├── cart/             # Shopping cart
│       ├── order/            # Order list, detail
│       └── staff/            # Staff dashboard
│
├── staff-service/            # Port 8001
│   ├── staff_service/        # Django project settings
│   └── staff/                # Staff models, views, serializers, urls
│
├── manager-service/          # Port 8002
│   ├── manager_service/
│   └── manager/
│
├── customer-service/         # Port 8003
│   ├── customer_service/
│   └── customers/            # Customer, Address models/views/serializers
│
├── catalog-service/          # Port 8004
│   ├── catalog_service/
│   └── catalog/              # Category, Author, Publisher
│
├── book-service/             # Port 8005
│   ├── book_service/
│   └── books/                # Book, Image, Description, Rating, Inventory
│       ├── models.py         # 7 models
│       ├── views.py          # 7 ViewSets
│       ├── serializers.py    # 12 serializers
│       └── urls.py           # Router configuration
│
├── cart-service/             # Port 8006
│   ├── cart_service/
│   └── cart/                 # Cart, CartItem, SavedCart
│       ├── models.py         # 4 models
│       ├── views.py          # 4 ViewSets + 2 function views
│       ├── serializers.py    # 9 serializers
│       ├── services.py       # HTTP client for Book Service
│       └── urls.py
│
├── order-service/            # Port 8007
│   ├── order_service/
│   └── orders/               # Order, OrderItem
│
├── ship-service/             # Port 8008
│   ├── ship_service/
│   └── shipping/             # ShippingMethod, Shipment
│
├── pay-service/              # Port 8009
│   ├── pay_service/
│   └── payments/             # PaymentMethod, Payment
│
├── comment-rate-service/     # Port 8010
│   ├── comment_service/
│   └── reviews/              # Review
│
├── recommender-ai-service/   # Port 8011
│   ├── recommender_service/
│   └── recommendations/      # Recommendation (ML-based)
│
├── sql/
│   └── init_databases.sql    # Tạo 11 databases + sample data
├── create_databases.sql      # Script tạo databases
└── .env.example              # Biến môi trường mẫu
```

---

## 3. Thiết kế cơ sở dữ liệu

### 3.1. Mô hình Database per Service

Hệ thống sử dụng **11 cơ sở dữ liệu MySQL riêng biệt**, mỗi service một database. Đây là pattern Database per Service, đảm bảo tính độc lập giữa các service và cho phép mỗi service tự do chọn schema phù hợp.

| # | Database | Service | Bảng chính | Số bảng |
|---|----------|---------|-----------|---------|
| 1 | `staff_db` | Staff Service | `staff_staff`, `staff_inventorylog` | 2 |
| 2 | `catalog_db` | Catalog Service | `catalog_category`, `catalog_author`, `catalog_publisher` | 3 |
| 3 | `book_db` | Book Service | `books_book`, `books_bookimage`, `books_bookdescription`, `books_bookrating`, `books_bookinventory`, `books_bookstatus`, `books_booktag` | 7+ |
| 4 | `customer_db` | Customer Service | `customers_customer`, `customers_address` | 2 |
| 5 | `cart_db` | Cart Service | `carts_cart`, `carts_cartitem`, `carts_cartstatus`, `carts_savedcart` | 4 |
| 6 | `order_db` | Order Service | `orders_order`, `orders_orderitem` | 2 |
| 7 | `ship_db` | Ship Service | `shipping_shippingmethod`, `shipping_shipment` | 2 |
| 8 | `pay_db` | Pay Service | `payments_paymentmethod`, `payments_payment` | 2 |
| 9 | `comment_db` | Comment-Rate Service | `reviews_review` | 1 |
| 10 | `recommender_db` | Recommender AI Service | `recommendations_recommendation` | 1 |
| 11 | `manager_db` | Manager Service | (aggregated views) | 0 |

**Tổng cộng**: 11 databases, ~26 bảng.

### 3.2. Xử lý liên kết liên database

Do không thể dùng Foreign Key giữa các database, hệ thống áp dụng chiến lược **Reference by Value**:

```
book_db.books_book                    catalog_db.catalog_author
┌─────────────────────┐               ┌──────────────────┐
│ id (PK)             │               │ id (PK)          │
│ title               │    Ref by     │ name             │
│ author_id (INT) ────┼──── Value ───►│ bio              │
│ category_id (INT) ──┼──── Value ───►│ nationality      │
│ publisher_id (INT) ─┼──── Value ───►└──────────────────┘
│ price               │
└─────────────────────┘

cart_db.carts_cartitem                book_db.books_book
┌─────────────────────┐               ┌──────────────────┐
│ id (PK)             │               │ id (PK)          │
│ cart_id (FK local)  │    Ref by     │ title            │
│ book_id (INT) ──────┼──── Value ───►│ price            │
│ quantity            │    + HTTP     │ stock            │
│ unit_price          │               └──────────────────┘
└─────────────────────┘
```

- **Trong cùng database**: Sử dụng Foreign Key constraint (ví dụ: `carts_cartitem.cart_id` → `carts_cart.id`).
- **Liên database**: Lưu ID dưới dạng `IntegerField`, không có FK constraint. Khi cần dữ liệu chi tiết, service gọi HTTP đến service chứa dữ liệu.

### 3.3. Dữ liệu khởi tạo

Script `init_databases.sql` tạo sẵn dữ liệu mẫu cho toàn hệ thống:

| Loại dữ liệu | Số lượng | Chi tiết |
|--------------|----------|---------|
| Danh mục sách | 5 | Văn học, Kinh tế, Công nghệ, Tâm lý, Thiếu nhi |
| Tác giả | 5 | Nguyễn Nhật Ánh, Dale Carnegie, Robert C. Martin, Paulo Coelho, Haruki Murakami |
| Nhà xuất bản | 3 | NXB Trẻ, NXB Kim Đồng, NXB Tổng hợp |
| Sách | 10 | Từ 79,000₫ đến 380,000₫ |
| Khách hàng test | 1 | test@example.com |
| Phương thức thanh toán | 4 | COD, Bank Transfer, MoMo, VNPay |
| Phương thức vận chuyển | 3 | Tiêu chuẩn (25k), Nhanh (45k), Hỏa tốc (70k) |
| Staff admin | 1 | admin@bookhaven.vn (role: admin) |

### 3.4. Sơ đồ quan hệ giữa các database

```
                    ┌─────────────┐
                    │  staff_db   │
                    │ ─────────── │
                    │ staff       │◄─── inventory_log.staff_id
                    │ inventorylog│──── book_id ───────────┐
                    └─────────────┘                        │
                                                           ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐
│ catalog_db  │     │ customer_db │     │        book_db          │
│ ─────────── │     │ ─────────── │     │ ─────────────────────── │
│ category    │◄────│ customer    │     │ book (author_id,        │
│ author      │     │ address     │     │       category_id,      │
│ publisher   │     └──────┬──────┘     │       publisher_id)     │
└──────▲──────┘            │            │ book_image              │
       │                   │            │ book_description        │
       │ ref               │ ref        │ book_rating             │
       └───────────┐       │            │ book_inventory          │
                   │       │            └────────────▲────────────┘
                   │       │                         │
                   │       ▼              ref        │
              ┌────┴────────────┐   ┌────────────────┘
              │    cart_db      │   │
              │ ────────────    │   │
              │ cart ───────────┼───┘ cart_item.book_id→book
              │ cart_item       │
              │ saved_cart      │
              └────────┬───────┘
                       │ cart → order
                       ▼
              ┌─────────────────┐
              │    order_db     │
              │ ─────────────── │
              │ order           │──────┬──────────────┐
              │ order_item      │      │              │
              └─────────────────┘      ▼              ▼
                                ┌────────────┐ ┌────────────┐
                                │  ship_db   │ │  pay_db    │
                                │ ────────── │ │ ────────── │
                                │ shipment   │ │ payment    │
                                │ ship_method│ │ pay_method │
                                └────────────┘ └────────────┘
```

---

## 4. Chi tiết các dịch vụ

### 4.1. Book Service (Port 8005) — Dịch vụ hoàn chỉnh nhất

Book Service là dịch vụ phức tạp và hoàn chỉnh nhất trong hệ thống, minh họa đầy đủ mô hình microservice với Django REST Framework.

#### 4.1.1. Models (7 models)

| Model | Quan hệ | Mô tả |
|-------|---------|-------|
| `BookStatus` | - | Trạng thái sách: Available, Out of Stock, Discontinued, ... |
| `BookTag` | M2M với Book | Tags phân loại: Bestseller, New Arrival, Sale, ... |
| `Book` | FK→BookStatus, M2M→BookTag | Sách. `author_id`, `category_id`, `publisher_id` là IntegerField (ref sang Catalog Service) |
| `BookImage` | FK→Book | Nhiều hình ảnh/sách, `is_primary` đánh dấu ảnh chính, `display_order` sắp xếp |
| `BookDescription` | OneToOne→Book | Mô tả chi tiết + tóm tắt (short_description) |
| `BookRating` | OneToOne→Book | `avg_score` (Decimal), `total_ratings`. Method `update_rating(new_score)` tính lại trung bình |
| `BookInventory` | OneToOne→Book | `quantity`, `min_stock_level`, `max_stock_level`, `reorder_point`, `last_restocked`. Methods: `add_stock()`, `reduce_stock()`, `check_stock()` trả về dict đầy đủ trạng thái |

#### 4.1.2. ViewSets (7 ViewSets)

**BookViewSet** — ViewSet chính, hỗ trợ đầy đủ CRUD và 15 query parameters:

| Parameter | Kiểu | Filter |
|-----------|------|--------|
| `title` | string | `icontains` (tìm kiếm mờ) |
| `isbn` | string | `icontains` |
| `author_id` | int | exact match |
| `category_id` | int | exact match |
| `publisher_id` | int | exact match |
| `status_id` | int | exact match |
| `available` | bool | kiểm tra `inventory__quantity > 0` |
| `tag_id` | int | `tags__tag_id` |
| `language` | string | exact match |
| `min_price` / `max_price` | decimal | range filter |
| `ordering` | string | `title`, `price`, `publication_date`, `created_at` (thêm `-` giảm dần) |
| `search` | string | `SearchFilter` trên title, isbn |

Custom actions:
- `GET /api/books/{id}/full_details/`: Trả về Book + tất cả images, description, rating, inventory trong một response duy nhất.
- `POST /api/books/{id}/update_rating/`: Cập nhật điểm đánh giá trung bình.
- `GET /api/books/search/?q=keyword`: Tìm kiếm nâng cao.

**BookInventoryViewSet** — Quản lý tồn kho với 5 custom actions:
- `POST /{id}/add_stock/`: Nhập thêm hàng (kiểm tra `amount > 0`).
- `POST /{id}/reduce_stock/`: Giảm tồn kho (kiểm tra đủ hàng).
- `GET /{id}/check_stock/`: Trả về trạng thái tồn kho chi tiết.
- `GET /low_stock_alerts/`: Danh sách sách sắp hết hàng.
- `POST /bulk_check/`: Kiểm tra tồn kho hàng loạt (nhận mảng `book_ids`).

**BookImageViewSet** — CRUD hình ảnh + `POST /{id}/set_primary/` (reset `is_primary` của tất cả ảnh cùng sách, đặt ảnh hiện tại làm ảnh chính).

**BookStatusViewSet, BookTagViewSet, BookDescriptionViewSet, BookRatingViewSet** — Standard CRUD operations.

#### 4.1.3. Serializers (12 serializers)

| Serializer | Dùng cho | Đặc điểm |
|-----------|---------|----------|
| `BookListSerializer` | GET danh sách | Nested tags, primary_image, computed `in_stock` field |
| `BookDetailSerializer` | GET chi tiết | Nested tất cả: images, description, rating, inventory (với `stock_status`) |
| `BookCreateUpdateSerializer` | POST/PUT | Tự động tạo `BookInventory` + `BookRating` khi tạo sách mới (signal trong `create()`) |
| `StockOperationSerializer` | add/reduce stock | Validate `amount > 0` |
| `BookRatingUpdateSerializer` | update_rating | Validate `score >= 0` |

### 4.2. Cart Service (Port 8006)

#### 4.2.1. Models (4 models)

| Model | Mô tả |
|-------|-------|
| `CartStatus` | Trạng thái: `active`, `checked_out`, `abandoned` |
| `Cart` | `customer_id` (IntegerField), FK→CartStatus. Properties: `total_items`, `total_price`. Method: `calculate_total()` |
| `CartItem` | FK→Cart, `book_id` (IntegerField), `unit_price`, `quantity`. Property: `subtotal` = quantity × unit_price |
| `SavedCart` | `customer_id`, `name`, `cart_data` (JSONField lưu snapshot giỏ hàng) |

#### 4.2.2. ViewSets và Endpoints

**CartViewSet** — 5 custom actions tích hợp giao tiếp liên service:

| Action | Method | Mô tả |
|--------|--------|-------|
| `add_item` | POST | Gọi Book Service kiểm tra tồn kho → tạo/cập nhật CartItem |
| `update_item` | PUT | Cập nhật số lượng (xóa nếu quantity = 0) |
| `remove_item` | DELETE | Xóa CartItem khỏi giỏ |
| `clear` | POST | Xóa toàn bộ items trong giỏ |
| `save_cart` | POST | Chuyển giỏ thành SavedCart (JSON snapshot) |

**SavedCartViewSet** — CRUD + `restore_cart` (khôi phục giỏ hàng từ JSON snapshot).

**Function-based views đặc biệt**:
- `POST /api/create-for-customer/`: Endpoint nội bộ, Customer Service gọi khi khách mới đăng ký → tạo giỏ hàng active.
- `GET /api/active-cart/?customer_id=N`: Lấy giỏ hàng đang hoạt động của một khách hàng.

### 4.3. Customer Service (Port 8003)

| Chức năng | Endpoint | Mô tả |
|-----------|----------|-------|
| Đăng ký | `POST /api/register/` | Tạo customer + gọi Cart Service tạo giỏ hàng |
| Đăng nhập | `POST /api/login/` | Xác thực → trả JWT token (hết hạn 24h) |
| Đăng xuất | `POST /api/logout/` | Vô hiệu hóa token |
| Profile | `GET/PUT /api/profile/` | Xem và cập nhật thông tin |
| Địa chỉ | CRUD `/api/addresses/` | Quản lý địa chỉ giao hàng, `is_default` |

Database: `customer_db` — 2 bảng: `customers_customer` (name, email, phone, password SHA256), `customers_address` (FK→customer, address, city, district, ward, is_default).

### 4.4. Catalog Service (Port 8004)

Dịch vụ **dữ liệu master**, quản lý metadata chung cho toàn hệ thống:

- `GET/POST /api/categories/` — Danh mục sách (5 danh mục ban đầu).
- `GET/POST /api/authors/` — Tác giả (name, bio, nationality).
- `GET/POST /api/publishers/` — Nhà xuất bản (name, address, phone).

Book Service tham chiếu đến Catalog Service qua `author_id`, `category_id`, `publisher_id` (IntegerField).

### 4.5. Order Service (Port 8007)

Quản lý toàn bộ vòng đời đơn hàng:

| Trạng thái | Mô tả |
|------------|-------|
| `pending` | Mới tạo, chờ xác nhận |
| `confirmed` | Đã xác nhận |
| `processing` | Đang xử lý |
| `shipped` | Đã giao cho vận chuyển |
| `delivered` | Đã giao thành công |
| `cancelled` | Đã hủy |

Database: `order_db` — `orders_order` (order_number, customer_id, shipping_address, subtotal, shipping_fee, discount, total, status), `orders_orderitem` (order_id FK, book_id, book_title, quantity, price).

### 4.6. Pay Service (Port 8009)

Hỗ trợ 4 phương thức thanh toán:

| Code | Phương thức | Mô tả |
|------|------------|-------|
| `cod` | Thanh toán khi nhận hàng | Trả tiền mặt khi nhận hàng |
| `bank` | Chuyển khoản ngân hàng | Chuyển khoản qua tài khoản ngân hàng |
| `momo` | Ví điện tử MoMo | Thanh toán qua ví điện tử MoMo |
| `vnpay` | Cổng thanh toán VNPay | Thanh toán qua cổng VNPay |

Trạng thái thanh toán: `pending` → `completed` | `failed` | `refunded`.  
Khi xử lý thành công, tạo `transaction_id` duy nhất (UUID) và ghi nhận `paid_at`.

### 4.7. Ship Service (Port 8008)

3 phương thức vận chuyển:

| Phương thức | Phí | Thời gian |
|------------|-----|-----------|
| Giao hàng tiêu chuẩn | 25,000₫ | 3–5 ngày |
| Giao hàng nhanh | 45,000₫ | 1–2 ngày |
| Giao hàng hỏa tốc | 70,000₫ | Trong ngày |

Trạng thái vận đơn: `pending` → `shipped` → `in_transit` → `delivered` | `returned`.

### 4.8. Comment-Rate Service (Port 8010)

- `POST /api/reviews/`: Tạo đánh giá (rating 1–5, title, content). `is_approved = false` mặc định → cần staff phê duyệt.
- Sau khi tạo review, gọi HTTP đến Book Service `POST /api/books/{id}/update_rating/` để cập nhật `avg_score`.
- Filter: `?book_id=N`, `?customer_id=N`.

### 4.9. Recommender AI Service (Port 8011)

Sử dụng thư viện ML (NumPy, scikit-learn) để gợi ý sách:

- `GET /api/recommendations/?customer_id=N`: Gợi ý cá nhân hóa (dựa trên lịch sử mua + sở thích thể loại).
- `GET /api/trending/`: Sách đang thịnh hành (nhiều đơn hàng gần đây).
- `GET /api/best-rated/`: Sách được đánh giá cao nhất.
- `GET /api/similar/{book_id}/`: Sách tương tự (cùng tác giả, danh mục, tags).

### 4.10. Staff Service (Port 8001) & Manager Service (Port 8002)

**Staff Service**: Xác thực nhân viên (JWT), quản lý nhân viên (3 roles: admin, manager, staff), ghi log thao tác kho (`staff_inventorylog`).

**Manager Service**: Dashboard tổng quan, báo cáo doanh thu, báo cáo tồn kho. Aggregates data từ các services khác.

---

## 5. API Gateway

### 5.1. Vai trò

API Gateway (port 8000) là **điểm vào duy nhất** của hệ thống, đóng 3 vai trò chính:

**1. Reverse Proxy**: Chuyển tiếp request từ client đến service tương ứng dựa trên URL prefix.  
**2. Web UI (Server-Side Rendering)**: Render HTML templates bằng Django Template Language, phục vụ giao diện web cho người dùng cuối.  
**3. Authentication Gateway**: Quản lý session, xác thực JWT token, và gắn thông tin user vào request trước khi forward.

### 5.2. Bảng định tuyến (Routing Table)

| URL Prefix | Service đích | Port | Mô tả |
|------------|-------------|------|-------|
| `/api/staff/` | Staff Service | 8001 | Quản lý nhân viên |
| `/api/manager/` | Manager Service | 8002 | Dashboard, báo cáo |
| `/api/customer/` | Customer Service | 8003 | Đăng ký, đăng nhập, profile |
| `/api/catalog/` | Catalog Service | 8004 | Danh mục, tác giả, NXB |
| `/api/books/` | Book Service | 8005 | Sách, tồn kho |
| `/api/cart/` | Cart Service | 8006 | Giỏ hàng |
| `/api/orders/` | Order Service | 8007 | Đơn hàng |
| `/api/shipping/` | Ship Service | 8008 | Vận chuyển |
| `/api/payment/` | Pay Service | 8009 | Thanh toán |
| `/api/comments/` | Comment-Rate Service | 8010 | Đánh giá |
| `/api/recommender/` | Recommender AI Service | 8011 | Gợi ý |

### 5.3. Web Templates

Gateway phục vụ giao diện web với hệ thống template Bootstrap 5:

```
templates/
├── base.html              # Layout chung (navbar, footer)
├── accounts/
│   ├── login.html         # Form đăng nhập
│   ├── register.html      # Form đăng ký
│   └── profile.html       # Trang cá nhân
├── books/
│   ├── catalog.html       # Danh sách sách (grid, tìm kiếm, lọc)
│   └── detail.html        # Chi tiết sách (hình ảnh, mô tả, đánh giá)
├── cart/
│   └── cart.html          # Giỏ hàng (danh sách, cập nhật, checkout)
├── order/
│   ├── list.html          # Lịch sử đơn hàng
│   └── detail.html        # Chi tiết đơn hàng
└── staff/
    ├── dashboard.html     # Bảng điều khiển
    └── inventory.html     # Quản lý tồn kho
```

---

## 6. Giao tiếp liên dịch vụ

### 6.1. Mô hình: Synchronous HTTP/REST

Các service giao tiếp với nhau qua **HTTP REST calls đồng bộ**. Mỗi service là một HTTP client có thể gọi đến service khác khi cần dữ liệu.

### 6.2. Sơ đồ giao tiếp liên service

```
┌──────────────┐     HTTP POST              ┌──────────────┐
│   Customer   │ ───────────────────────── ►│    Cart      │
│   Service    │  /api/create-for-customer/ │   Service    │
│   (:8003)    │  (khi đăng ký khách mới)  │   (:8006)    │
└──────────────┘                            └───────┬──────┘
                                                    │
                                           HTTP GET │
                                   /api/books/{id}/ │
                                                    ▼
┌──────────────┐                            ┌──────────────┐
│  Comment     │     HTTP POST              │    Book      │
│  Rate Svc    │ ──────────────────────── ► │   Service    │
│  (:8010)     │  /api/books/{id}/          │   (:8005)    │
└──────────────┘   update_rating/           └──────────────┘
                                                    ▲
                                           HTTP GET │
                                   /api/inventory/  │  
┌──────────────┐    bulk_check/             ┌───────┴──────┐
│   Order      │ ──────────────────────── ► │    Book      │
│   Service    │                            │   Service    │
│   (:8007)    │ ──────────────────────── ► │              │
└──────────────┘  /api/inventory/{id}/      └──────────────┘
       │            reduce_stock/
       │
       ├──── HTTP POST ──── ► Cart Svc   (đóng giỏ hàng)
       ├──── HTTP POST ──── ► Pay Svc    (tạo thanh toán)
       └──── HTTP POST ──── ► Ship Svc   (tạo vận đơn)
```

### 6.3. Ví dụ: Cart Service gọi Book Service

Khi khách hàng thêm sách vào giỏ, Cart Service cần xác minh sách tồn tại và còn hàng:

```python
# cart-service/cart/services.py
import requests

BOOK_SERVICE_URL = "http://localhost:8005/api"

class BookServiceClient:
    def verify_book_availability(self, book_id):
        """Gọi Book Service kiểm tra sách còn hàng không"""
        try:
            response = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/")
            if response.status_code == 200:
                book_data = response.json()
                return {
                    "exists": True,
                    "title": book_data["title"],
                    "price": book_data["price"],
                    "in_stock": book_data.get("in_stock", True)
                }
        except requests.ConnectionError:
            pass  # Book Service unavailable
        return {"exists": False}
```

```python
# cart-service/cart/views.py (add_item action)
@action(detail=True, methods=['post'])
def add_item(self, request, pk=None):
    cart = self.get_object()
    book_id = request.data.get('book_id')
    quantity = request.data.get('quantity', 1)
    
    # Gọi Book Service
    book_info = book_service_client.verify_book_availability(book_id)
    
    if book_info.get("exists"):
        unit_price = book_info.get("price", "0.00")
    else:
        unit_price = "0.00"  # Graceful degradation
    
    # Tạo hoặc cập nhật CartItem
    item, created = CartItem.objects.get_or_create(
        cart=cart, book_id=book_id,
        defaults={"unit_price": unit_price, "quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()
    
    return Response(CartSerializer(cart).data)
```

### 6.4. Ví dụ: Customer Service gọi Cart Service

Khi khách hàng đăng ký thành công, Customer Service tự động tạo giỏ hàng:

```python
# customer-service (trong register view)
import requests

def register(request):
    # ... tạo customer ...
    
    # Gọi Cart Service tạo giỏ hàng
    try:
        requests.post(
            "http://localhost:8006/api/create-for-customer/",
            json={"customer_id": customer.id}
        )
    except requests.ConnectionError:
        pass  # Cart Service unavailable, giỏ hàng sẽ được tạo sau
```

---

## 7. Xác thực và phân quyền

### 7.1. JWT Authentication

Hệ thống sử dụng **JSON Web Token (JWT)** với thuật toán **HS256** cho xác thực:

```
┌──────────┐  POST /api/login/   ┌──────────────┐
│  Client  │ ──────────────────► │  Customer/   │
│          │  {email, password}  │  Staff Svc   │
│          │ ◄────────────────── │              │
│          │  {token: "eyJ..."}  └──────────────┘
│          │
│          │  GET /api/books/     ┌──────────────┐
│          │ ──────────────────► │ API Gateway  │
│          │  Authorization:     │              │
│          │  Bearer eyJ...      │  → Verify    │
│          │                     │  → Forward   │
└──────────┘                     └──────────────┘
```

**Thông số JWT**:
- Algorithm: HS256 (HMAC-SHA256)
- Thời hạn: 24 giờ
- Payload: `customer_id` hoặc `staff_id`, `email`, `role`, `exp`, `iat`

### 7.2. Phân quyền theo vai trò

| Vai trò | Service xác thực | Quyền truy cập |
|---------|-----------------|----------------|
| Customer | Customer Service | Books (đọc), Cart (CRUD), Order (tạo/xem), Review (tạo), Profile (CRUD) |
| Staff | Staff Service | Inventory (thêm/giảm stock), Books (CRUD), Inventory Logs (xem) |
| Manager | Manager Service | Dashboard, Reports, Staff management |
| Admin | Staff Service | Toàn quyền |

### 7.3. Giao tiếp nội bộ (Inter-service)

Các service gọi lẫn nhau trong mạng nội bộ **không yêu cầu JWT**. Đây là thiết kế tin tưởng mạng nội bộ (trusted internal network), phù hợp cho môi trường Docker/Kubernetes nơi các service không expose ra ngoài.

---

## 8. Thiết kế RESTful API

### 8.1. Quy ước chung

| Thuộc tính | Giá trị |
|------------|---------|
| Content-Type | `application/json` |
| Pagination | 20 items/page, query `?page=N` |
| Charset | UTF-8 |
| Tiền tệ | VND (không thập phân, kiểu `DECIMAL(12,0)`) |
| URL Convention | `/api/{resource}/` (danh sách), `/api/{resource}/{id}/` (chi tiết) |
| Naming | Lowercase, plural nouns (books, carts, orders) |

### 8.2. HTTP Methods

| Method | Mục đích | Response Code |
|--------|---------|--------------|
| `GET` | Đọc dữ liệu | 200 OK |
| `POST` | Tạo mới | 201 Created |
| `PUT` | Cập nhật toàn bộ | 200 OK |
| `PATCH` | Cập nhật một phần | 200 OK |
| `DELETE` | Xóa | 204 No Content |

### 8.3. Cấu trúc Response

**Thành công (danh sách, có pagination)**:
```json
{
  "count": 10,
  "next": "http://localhost:8005/api/books/?page=2",
  "previous": null,
  "results": [
    {"book_id": 1, "title": "...", "price": "85000.00"}
  ]
}
```

**Thành công (chi tiết)**:
```json
{
  "book_id": 1,
  "title": "Cho tôi xin một vé đi tuổi thơ",
  "price": "85000.00",
  "author_id": 1
}
```

**Lỗi validation**:
```json
{
  "field_name": ["Thông báo lỗi."],
  "quantity": ["Ensure this value is greater than or equal to 1."]
}
```

**Lỗi chung**:
```json
{
  "error": "Not found.",
  "detail": "Book with id 999 does not exist."
}
```

### 8.4. Mã lỗi HTTP

| Status | Ý nghĩa | Khi nào trả |
|--------|---------|------------|
| 200 | Thành công | GET, PUT, PATCH |
| 201 | Tạo thành công | POST |
| 204 | Xóa thành công | DELETE |
| 400 | Request không hợp lệ | Validation error, thiếu field bắt buộc |
| 401 | Chưa xác thực | Token hết hạn hoặc không hợp lệ |
| 403 | Không có quyền | Staff truy cập API admin |
| 404 | Không tìm thấy | ID không tồn tại |
| 500 | Lỗi server | Exception chưa xử lý |

---

## 9. Xử lý lỗi và Fault Tolerance

### 9.1. Graceful Degradation

Khi một service không khả dụng, các service phụ thuộc không bị crash mà xử lý gracefully:

**Trường hợp: Book Service không phản hồi khi Cart Service thêm sản phẩm**
```
Cart Service → HTTP GET Book Service (:8005)
             → ConnectionError / Timeout
             → Fallback: unit_price = 0.00, vẫn thêm vào giỏ
             → Giá sẽ được cập nhật khi checkout (Order Service gọi lại Book Service)
```

**Trường hợp: Cart Service không phản hồi khi Customer đăng ký**
```
Customer Service → POST /api/create-for-customer/
                → ConnectionError
                → Customer vẫn được tạo thành công
                → Giỏ hàng sẽ được tạo tự động khi khách truy cập cart lần đầu
```

### 9.2. Timeout và Retry

Các HTTP call liên service được cấu hình:
- **Connection timeout**: 5 giây
- **Read timeout**: 10 giây
- **Retry**: Không retry tự động (để tránh cascading failures)

### 9.3. Error Logging

Mỗi service ghi log riêng biệt qua Django logging framework, bao gồm:
- Request/response logging cho inter-service calls
- Exception stack traces
- Timeout và connection errors

---

## 10. Triển khai và vận hành

### 10.1. Yêu cầu hệ thống

| Thành phần | Yêu cầu tối thiểu |
|------------|-------------------|
| Python | 3.10+ |
| MySQL | 8.0+ |
| RAM | 4 GB (12 services đồng thời) |
| Disk | 1 GB |
| OS | Windows 10+, Linux, macOS |

### 10.2. Hướng dẫn triển khai

**Bước 1: Khởi tạo toàn bộ 11 databases**
```bash
mysql -u root -p < micro/sql/init_databases.sql
```

Script này tạo 11 databases (`staff_db`, `catalog_db`, `book_db`, `customer_db`, `cart_db`, `order_db`, `ship_db`, `pay_db`, `comment_db`, `recommender_db`, `manager_db`) cùng dữ liệu mẫu.

**Bước 2: Cấu hình biến môi trường**
```bash
cp micro/.env.example micro/.env
# Chỉnh sửa DB_PASSWORD, SECRET_KEY, ...
```

Nội dung `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
SECRET_KEY=your-secret-key
DEBUG=True
```

**Bước 3: Cài đặt và chạy từng service**
```bash
# Mỗi service là một Django project độc lập
cd micro/book-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8005

# Tương tự cho các service khác, thay đổi thư mục và port
```

**Bước 4: Hoặc chạy tất cả bằng script tự động**
```bash
python micro/run_local.py
# Script khởi động tất cả 12 services trên các port 8000-8011
```

### 10.3. Cấu hình Port

| Service | Port | Khởi động |
|---------|------|-----------|
| API Gateway | 8000 | `python manage.py runserver 8000` |
| Staff Service | 8001 | `python manage.py runserver 8001` |
| Manager Service | 8002 | `python manage.py runserver 8002` |
| Customer Service | 8003 | `python manage.py runserver 8003` |
| Catalog Service | 8004 | `python manage.py runserver 8004` |
| Book Service | 8005 | `python manage.py runserver 8005` |
| Cart Service | 8006 | `python manage.py runserver 8006` |
| Order Service | 8007 | `python manage.py runserver 8007` |
| Ship Service | 8008 | `python manage.py runserver 8008` |
| Pay Service | 8009 | `python manage.py runserver 8009` |
| Comment-Rate | 8010 | `python manage.py runserver 8010` |
| Recommender AI | 8011 | `python manage.py runserver 8011` |

### 10.4. Docker Deployment

Mỗi service có `Dockerfile` riêng:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8005
CMD ["python", "manage.py", "runserver", "0.0.0.0:8005"]
```

### 10.5. Tài khoản test

| Vai trò | Email / Username | Mật khẩu |
|---------|-----------------|-----------|
| Khách hàng | customer1 | pass123 |
| Admin | admin@bookstore.com | admin123 |
| Staff | staff1@bookstore.com | staff123 |
| Manager | manager1@bookstore.com | manager123 |

---

## 11. Đánh giá kiến trúc

### 11.1. Ưu điểm

| Ưu điểm | Phân tích |
|---------|----------|
| **Scale độc lập** | Khi Book Service nhận nhiều traffic (search, catalog), chỉ cần scale Book Service mà không ảnh hưởng đến Cart hay Order |
| **Fault Isolation** | Nếu Recommender AI Service bị lỗi, khách hàng vẫn có thể duyệt sách, đặt hàng, thanh toán bình thường |
| **Polyglot Technology** | Mỗi service có thể dùng công nghệ khác nhau. Recommender AI dùng Python ML; trong tương lai, Book Service có thể chuyển sang Elasticsearch |
| **Deploy độc lập** | Cập nhật Pay Service (thêm phương thức thanh toán mới) không cần deploy lại 11 service còn lại |
| **Team Independence** | Mỗi team phụ trách 1–2 services, có thể phát triển song song không xung đột |
| **Database Isolation** | Mỗi service tự do tối ưu schema. Book Service có thể dùng full-text index; Cart Service có thể dùng Redis trong tương lai |

### 11.2. Nhược điểm

| Nhược điểm | Phân tích |
|-----------|----------|
| **Operational Complexity** | Phải quản lý 12 services + 11 databases. Theo dõi log, monitor health, restart khi lỗi |
| **Network Latency** | Mỗi inter-service call thêm ~10-50ms latency. Một luồng checkout cần 4-5 HTTP calls liên service |
| **Data Consistency** | Không có ACID transaction liên database. Nếu Order Service tạo đơn thành công nhưng Pay Service fail → inconsistency |
| **Distributed Debugging** | Lỗi xảy ra ở service nào? Cần centralized logging (ELK stack) và distributed tracing (Jaeger/Zipkin) |
| **Reference by Value** | Không có FK constraint liên database → có thể có book_id không tồn tại trong cart_db nếu sách bị xóa |
| **Infrastructure Cost** | 12 processes + 11 MySQL instances tiêu tốn tài nguyên nhiều hơn 1 monolith đáng kể |

### 11.3. Bài học kiến trúc

**1. Service Granularity**  
Hệ thống chia thành 12 services là khá chi tiết. Trong thực tế, có thể gom Staff + Manager thành một Admin Service, hoặc gom Ship + Pay thành Fulfillment Service để giảm operational overhead.

**2. Synchronous vs Asynchronous**  
Hiện tại toàn bộ giao tiếp là synchronous HTTP. Điểm yếu: cascading failures khi một service chậm. Giải pháp: áp dụng Message Queue (RabbitMQ/Kafka) cho các thao tác không cần response ngay (gửi email, cập nhật recommendation, ghi log).

**3. Data Duplication vs Data Referencing**  
Cart Service lưu `unit_price` tại thời điểm thêm vào giỏ → đảm bảo giá không đổi khi Book Service cập nhật giá. Đây là trade-off giữa consistency và independence.

---

## 12. Kết luận và hướng phát triển

### 12.1. Kết quả đạt được

Dự án đã triển khai thành công hệ thống nhà sách trực tuyến theo kiến trúc microservices với:

- **12 dịch vụ độc lập**, mỗi dịch vụ có database, API, và lifecycle riêng.
- **11 cơ sở dữ liệu MySQL** theo pattern Database per Service.
- **RESTful API** chuẩn với Django REST Framework: ViewSets, Serializers, Router, Filtering, Pagination.
- **Giao tiếp liên service** qua HTTP REST với graceful degradation.
- **API Gateway** vừa làm reverse proxy vừa phục vụ giao diện web (SSR).
- **Xác thực JWT** cho customer và staff.
- **Giao diện web** responsive với Bootstrap 5.
- **AI Recommendation** Service sử dụng machine learning.

### 12.2. Hướng phát triển

| Hạng mục | Giải pháp đề xuất | Ưu tiên |
|----------|-------------------|---------|
| Container Orchestration | Docker Compose / Kubernetes | Cao |
| Async Communication | RabbitMQ / Apache Kafka cho event-driven | Cao |
| Circuit Breaker | Implement Circuit Breaker pattern (retry + fallback) | Cao |
| Centralized Logging | ELK Stack (Elasticsearch + Logstash + Kibana) | Trung bình |
| Distributed Tracing | Jaeger hoặc Zipkin | Trung bình |
| API Rate Limiting | Django REST Framework throttling + Redis | Trung bình |
| Monitoring | Prometheus + Grafana dashboard | Trung bình |
| CI/CD | GitHub Actions pipeline riêng cho từng service | Trung bình |
| Caching | Redis cho catalog data, session, rate limiting | Thấp |
| Full-text Search | Elasticsearch cho Book Service search | Thấp |
| Hoàn thiện services | Implement đầy đủ logic cho các skeleton services | Cao |

### 12.3. Tổng kết

Kiến trúc microservices mang lại khả năng **mở rộng linh hoạt**, **cách ly lỗi**, và **phát triển độc lập** — phù hợp cho hệ thống lớn với nhiều team. Tuy nhiên, đi kèm là chi phí vận hành cao hơn và phức tạp trong xử lý dữ liệu phân tán. Qua dự án này, ta thấy rõ rằng việc lựa chọn kiến trúc phần mềm không phải là chọn "tốt nhất" mà là chọn **phù hợp nhất** với quy mô, đội ngũ, và yêu cầu của dự án.

---

*Báo cáo được viết dựa trên phân tích mã nguồn thực tế của dự án assignment_01 — phiên bản Microservices.*