# 📖 BookStore Microservices — API Documentation

> **Base URL**: `http://localhost:8000/api/{service}/`  
> **Gateway Port**: 8000  
> **Routing Pattern**: `GET/POST/PUT/DELETE http://localhost:8000/api/{service}/{path}` → proxy tới `http://localhost:{port}/api/{path}`

---

## Mục lục

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Book Service API (Port 8005)](#2-book-service-api-port-8005)
3. [Cart Service API (Port 8006)](#3-cart-service-api-port-8006)
4. [Catalog Service API (Port 8004)](#4-catalog-service-api-port-8004)
5. [Customer Service API (Port 8003)](#5-customer-service-api-port-8003)
6. [Order Service API (Port 8007)](#6-order-service-api-port-8007)
7. [Pay Service API (Port 8009)](#7-pay-service-api-port-8009)
8. [Ship Service API (Port 8008)](#8-ship-service-api-port-8008)
9. [Comment-Rate Service API (Port 8010)](#9-comment-rate-service-api-port-8010)
10. [Recommender AI Service API (Port 8011)](#10-recommender-ai-service-api-port-8011)
11. [Staff Service API (Port 8001)](#11-staff-service-api-port-8001)
12. [Manager Service API (Port 8002)](#12-manager-service-api-port-8002)
13. [Mã lỗi chung](#13-mã-lỗi-chung)

---

## 1. Tổng quan kiến trúc

### Sơ đồ định tuyến API Gateway

```
Client (Browser/Mobile)
       │
       ▼
┌──────────────────────┐
│  API Gateway (:8000) │
│  /api/{service}/...  │
└──────┬───────────────┘
       │  HTTP Proxy
       ├──► staff-service     (:8001)  →  /api/staff/...
       ├──► manager-service   (:8002)  →  /api/manager/...
       ├──► customer-service  (:8003)  →  /api/customer/...
       ├──► catalog-service   (:8004)  →  /api/catalog/...
       ├──► book-service      (:8005)  →  /api/books/...
       ├──► cart-service      (:8006)  →  /api/cart/...
       ├──► order-service     (:8007)  →  /api/orders/...
       ├──► ship-service      (:8008)  →  /api/shipping/...
       ├──► pay-service       (:8009)  →  /api/payment/...
       ├──► comment-service   (:8010)  →  /api/comments/...
       └──► recommender       (:8011)  →  /api/recommender/...
```

### Quy ước chung

| Thuộc tính | Giá trị |
|---|---|
| Content-Type | `application/json` |
| Pagination | 20 items/page mặc định, query param `?page=N` |
| Authentication | JWT Token (header `Authorization: Bearer <token>`) |
| Charset | UTF-8 |
| Tiền tệ | VND (không thập phân) |

---

## 2. Book Service API (Port 8005)

**Base URL**: `http://localhost:8005/api/`  
**Database**: `book_db` (MySQL)

### 2.1. Book Statuses

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/statuses/` | Lấy danh sách trạng thái sách |
| `POST` | `/api/statuses/` | Tạo trạng thái mới |
| `GET` | `/api/statuses/{status_id}/` | Lấy chi tiết một trạng thái |
| `PUT` | `/api/statuses/{status_id}/` | Cập nhật trạng thái |
| `DELETE` | `/api/statuses/{status_id}/` | Xóa trạng thái |

**Response Body** (`GET /api/statuses/`):
```json
[
  {
    "status_id": 1,
    "status_name": "Available",
    "description": "Sách đang có sẵn"
  }
]
```

### 2.2. Book Tags

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/tags/` | Lấy danh sách tags (hỗ trợ `?search=keyword`) |
| `POST` | `/api/tags/` | Tạo tag mới |
| `GET` | `/api/tags/{tag_id}/` | Lấy chi tiết tag |
| `PUT` | `/api/tags/{tag_id}/` | Cập nhật tag |
| `DELETE` | `/api/tags/{tag_id}/` | Xóa tag |

**Request Body** (`POST /api/tags/`):
```json
{
  "name": "Bestseller",
  "description": "Sách bán chạy"
}
```

### 2.3. Books (CRUD + Tìm kiếm)

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/books/` | Lấy danh sách sách (có filter & pagination) |
| `POST` | `/api/books/` | Thêm sách mới |
| `GET` | `/api/books/{book_id}/` | Lấy chi tiết sách (đầy đủ thông tin) |
| `PUT` | `/api/books/{book_id}/` | Cập nhật sách |
| `PATCH` | `/api/books/{book_id}/` | Cập nhật một phần sách |
| `DELETE` | `/api/books/{book_id}/` | Xóa sách |
| `GET` | `/api/books/{book_id}/full_details/` | Lấy thông tin đầy đủ (images, description, rating, inventory) |
| `POST` | `/api/books/{book_id}/update_rating/` | Cập nhật điểm đánh giá sách |
| `GET` | `/api/books/search/` | Tìm kiếm nâng cao |

#### Query Parameters cho `GET /api/books/`

| Parameter | Type | Mô tả |
|-----------|------|--------|
| `title` | string | Lọc theo tên sách (icontains) |
| `isbn` | string | Lọc theo ISBN (icontains) |
| `author_id` | int | Lọc theo ID tác giả |
| `category_id` | int | Lọc theo ID danh mục |
| `publisher_id` | int | Lọc theo ID nhà xuất bản |
| `status_id` | int | Lọc theo trạng thái |
| `available` | bool | Lọc sách còn hàng (`true`/`false`) |
| `tag_id` | int | Lọc theo tag |
| `language` | string | Lọc theo ngôn ngữ |
| `min_price` | decimal | Giá tối thiểu |
| `max_price` | decimal | Giá tối đa |
| `ordering` | string | Sắp xếp: `title`, `price`, `publication_date`, `created_at` (thêm `-` để giảm dần) |
| `search` | string | Tìm theo title, isbn |
| `page` | int | Số trang |

#### Ví dụ Request/Response

**Request**: `GET /api/books/?category_id=1&available=true&ordering=-price`

**Response** (`GET /api/books/` — danh sách):
```json
{
  "count": 10,
  "next": "http://localhost:8005/api/books/?page=2",
  "previous": null,
  "results": [
    {
      "book_id": 1,
      "title": "Cho tôi xin một vé đi tuổi thơ",
      "isbn": "978-604-1",
      "price": "85000.00",
      "author_id": 1,
      "category_id": 1,
      "publisher_id": 1,
      "status": {
        "status_id": 1,
        "status_name": "Available",
        "description": null
      },
      "publication_date": "2008-01-01",
      "pages": 216,
      "language": "Vietnamese",
      "tags": [
        {"tag_id": 1, "name": "Bestseller", "description": null}
      ],
      "primary_image": {
        "image_id": 1,
        "url": "https://example.com/book1.jpg",
        "alt_text": "Cover",
        "is_primary": true,
        "display_order": 0
      },
      "in_stock": true,
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

**Response** (`GET /api/books/{id}/` — chi tiết):
```json
{
  "book_id": 1,
  "title": "Cho tôi xin một vé đi tuổi thơ",
  "isbn": "978-604-1",
  "price": "85000.00",
  "author_id": 1,
  "category_id": 1,
  "publisher_id": 1,
  "status": {"status_id": 1, "status_name": "Available"},
  "publication_date": "2008-01-01",
  "pages": 216,
  "language": "Vietnamese",
  "tags": [{"tag_id": 1, "name": "Bestseller"}],
  "images": [
    {"image_id": 1, "url": "https://...", "alt_text": "Cover", "is_primary": true, "display_order": 0}
  ],
  "description": {
    "desc_id": 1,
    "content": "Tác phẩm nổi tiếng...",
    "short_description": "Sách về tuổi thơ"
  },
  "rating": {
    "rating_id": 1,
    "avg_score": "4.50",
    "total_ratings": 20
  },
  "inventory": {
    "inventory_id": 1,
    "quantity": 50,
    "min_stock_level": 5,
    "max_stock_level": 100,
    "reorder_point": 10,
    "last_restocked": "2026-01-01T00:00:00Z",
    "stock_status": {
      "book_id": 1,
      "quantity": 50,
      "in_stock": true,
      "low_stock": false,
      "needs_reorder": false
    }
  },
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**Request**: `POST /api/books/`
```json
{
  "title": "Clean Code",
  "isbn": "978-0-13-235088-4",
  "price": "350000.00",
  "author_id": 3,
  "category_id": 3,
  "publisher_id": 2,
  "status": 1,
  "publication_date": "2008-08-01",
  "pages": 464,
  "language": "English",
  "tag_ids": [1, 2]
}
```

**Request**: `POST /api/books/{id}/update_rating/`
```json
{
  "score": "4.50"
}
```

**Request**: `GET /api/books/search/?q=python&category_id=3`

### 2.4. Book Images

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/images/` | Lấy danh sách ảnh (`?book_id=N` để lọc) |
| `POST` | `/api/images/` | Thêm ảnh cho sách |
| `GET` | `/api/images/{image_id}/` | Lấy chi tiết ảnh |
| `PUT` | `/api/images/{image_id}/` | Cập nhật ảnh |
| `DELETE` | `/api/images/{image_id}/` | Xóa ảnh |
| `POST` | `/api/images/{image_id}/set_primary/` | Đặt làm ảnh chính |

**Request Body** (`POST /api/images/`):
```json
{
  "book": 1,
  "url": "https://example.com/image.jpg",
  "alt_text": "Book Cover",
  "is_primary": true,
  "display_order": 0
}
```

### 2.5. Book Descriptions

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/descriptions/` | Lấy danh sách mô tả (`?book_id=N`) |
| `POST` | `/api/descriptions/` | Tạo mô tả cho sách |
| `GET` | `/api/descriptions/{desc_id}/` | Lấy chi tiết mô tả |
| `PUT` | `/api/descriptions/{desc_id}/` | Cập nhật mô tả |
| `DELETE` | `/api/descriptions/{desc_id}/` | Xóa mô tả |

**Request Body** (`POST /api/descriptions/`):
```json
{
  "book": 1,
  "content": "Nội dung chi tiết về sách...",
  "short_description": "Mô tả ngắn"
}
```

### 2.6. Book Ratings (Chỉ đọc)

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/ratings/` | Lấy danh sách đánh giá (`?book_id=N`) |
| `GET` | `/api/ratings/{rating_id}/` | Lấy chi tiết đánh giá |

> **Lưu ý**: Cập nhật rating qua `POST /api/books/{id}/update_rating/`

**Response**:
```json
{
  "rating_id": 1,
  "book": 1,
  "avg_score": "4.25",
  "total_ratings": 12
}
```

### 2.7. Book Inventory

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/inventory/` | Lấy danh sách tồn kho (`?book_id=N`, `?low_stock=true`, `?needs_reorder=true`) |
| `POST` | `/api/inventory/` | Tạo bản ghi tồn kho |
| `GET` | `/api/inventory/{inventory_id}/` | Chi tiết tồn kho |
| `PUT` | `/api/inventory/{inventory_id}/` | Cập nhật tồn kho |
| `POST` | `/api/inventory/{inventory_id}/add_stock/` | Nhập thêm hàng |
| `POST` | `/api/inventory/{inventory_id}/reduce_stock/` | Giảm tồn kho |
| `GET` | `/api/inventory/{inventory_id}/check_stock/` | Kiểm tra trạng thái tồn kho |
| `GET` | `/api/inventory/low_stock_alerts/` | Danh sách sách sắp hết hàng |
| `POST` | `/api/inventory/bulk_check/` | Kiểm tra tồn kho hàng loạt |

**Request**: `POST /api/inventory/{id}/add_stock/`
```json
{
  "amount": 50
}
```

**Response**:
```json
{
  "message": "Successfully added 50 units",
  "stock_status": {
    "book_id": 1,
    "quantity": 100,
    "in_stock": true,
    "low_stock": false,
    "needs_reorder": false,
    "min_stock_level": 5,
    "max_stock_level": 100,
    "reorder_point": 10,
    "last_restocked": "2026-03-10T09:00:00Z"
  }
}
```

**Request**: `POST /api/inventory/bulk_check/`
```json
{
  "book_ids": [1, 2, 3, 5]
}
```

---

## 3. Cart Service API (Port 8006)

**Base URL**: `http://localhost:8006/api/`  
**Database**: `cart_db` (MySQL)  
**Giao tiếp**: Gọi tới Book Service để kiểm tra tồn kho trước khi thêm vào giỏ

### 3.1. Cart Statuses

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/statuses/` | Lấy danh sách trạng thái giỏ hàng |
| `POST` | `/api/statuses/` | Tạo trạng thái mới |
| `GET` | `/api/statuses/{status_id}/` | Chi tiết trạng thái |
| `PUT` | `/api/statuses/{status_id}/` | Cập nhật trạng thái |
| `DELETE` | `/api/statuses/{status_id}/` | Xóa trạng thái |

**Trạng thái mặc định**: `active`, `checked_out`, `abandoned`

### 3.2. Carts

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/carts/` | Lấy danh sách giỏ hàng (`?customer_id=N`, `?is_active=true`) |
| `POST` | `/api/carts/` | Tạo giỏ hàng mới |
| `GET` | `/api/carts/{cart_id}/` | Chi tiết giỏ hàng (kèm items) |
| `PUT` | `/api/carts/{cart_id}/` | Cập nhật giỏ hàng |
| `DELETE` | `/api/carts/{cart_id}/` | Xóa giỏ hàng |
| `POST` | `/api/carts/{cart_id}/add_item/` | Thêm sản phẩm vào giỏ |
| `PUT` | `/api/carts/{cart_id}/update_item/{item_id}/` | Cập nhật số lượng sản phẩm |
| `DELETE` | `/api/carts/{cart_id}/remove_item/{item_id}/` | Xóa sản phẩm khỏi giỏ |
| `POST` | `/api/carts/{cart_id}/clear/` | Xóa toàn bộ sản phẩm trong giỏ |
| `POST` | `/api/carts/{cart_id}/save_cart/` | Lưu giỏ hàng để mua sau |

#### Thêm sản phẩm vào giỏ

**Request**: `POST /api/carts/{cart_id}/add_item/`
```json
{
  "book_id": 1,
  "quantity": 2
}
```

**Response**:
```json
{
  "cart_id": 1,
  "customer_id": 1,
  "status": {"status_id": 1, "name": "active", "description": "Active shopping cart"},
  "is_active": true,
  "items": [
    {
      "item_id": 1,
      "cart": 1,
      "book_id": 1,
      "quantity": 2,
      "unit_price": "85000.00",
      "subtotal": "170000.00",
      "added_at": "2026-03-10T09:00:00Z",
      "updated_at": "2026-03-10T09:00:00Z"
    }
  ],
  "total_items": 2,
  "total_price": "170000.00",
  "created_at": "2026-03-10T08:00:00Z",
  "updated_at": "2026-03-10T09:00:00Z"
}
```

#### Cập nhật số lượng

**Request**: `PUT /api/carts/{cart_id}/update_item/{item_id}/`
```json
{
  "quantity": 5
}
```

#### Lưu giỏ hàng

**Request**: `POST /api/carts/{cart_id}/save_cart/`
```json
{
  "name": "Giỏ hàng sinh nhật"
}
```

### 3.3. Cart Items

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/items/` | Danh sách items (`?cart_id=N`, `?book_id=N`) |
| `POST` | `/api/items/` | Tạo item trực tiếp |
| `GET` | `/api/items/{item_id}/` | Chi tiết item |
| `PUT` | `/api/items/{item_id}/` | Cập nhật item |
| `DELETE` | `/api/items/{item_id}/` | Xóa item |

### 3.4. Saved Carts

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/saved/` | Danh sách giỏ đã lưu (`?customer_id=N`) |
| `POST` | `/api/saved/` | Tạo saved cart |
| `GET` | `/api/saved/{saved_id}/` | Chi tiết saved cart |
| `DELETE` | `/api/saved/{saved_id}/` | Xóa saved cart |
| `POST` | `/api/saved/{saved_id}/restore_cart/` | Khôi phục giỏ hàng đã lưu |

### 3.5. Utility Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `POST` | `/api/create-for-customer/` | Tạo giỏ hàng cho khách hàng mới (gọi từ Customer Service) |
| `GET` | `/api/active-cart/?customer_id=N` | Lấy giỏ hàng đang hoạt động của khách |

**Request**: `POST /api/create-for-customer/`
```json
{
  "customer_id": 1
}
```

**Response**:
```json
{
  "message": "Cart created successfully",
  "cart": {
    "cart_id": 1,
    "customer_id": 1,
    "status": {"status_id": 1, "name": "active"},
    "is_active": true,
    "items": [],
    "total_items": 0,
    "total_price": "0.00"
  }
}
```

---

## 4. Catalog Service API (Port 8004)

**Base URL**: `http://localhost:8004/api/`  
**Database**: `catalog_db` (MySQL)

### 4.1. Categories

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/categories/` | Lấy danh sách danh mục |
| `POST` | `/api/categories/` | Tạo danh mục mới |
| `GET` | `/api/categories/{id}/` | Chi tiết danh mục |
| `PUT` | `/api/categories/{id}/` | Cập nhật danh mục |
| `DELETE` | `/api/categories/{id}/` | Xóa danh mục |

**Response**:
```json
[
  {"id": 1, "name": "Văn học", "description": "Sách văn học Việt Nam và thế giới", "is_active": true},
  {"id": 2, "name": "Kinh tế", "description": "Sách kinh tế, kinh doanh, quản trị", "is_active": true},
  {"id": 3, "name": "Công nghệ", "description": "Sách lập trình, IT, khoa học máy tính", "is_active": true},
  {"id": 4, "name": "Tâm lý", "description": "Sách tâm lý học, phát triển bản thân", "is_active": true},
  {"id": 5, "name": "Thiếu nhi", "description": "Sách dành cho trẻ em", "is_active": true}
]
```

### 4.2. Authors

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/authors/` | Lấy danh sách tác giả |
| `POST` | `/api/authors/` | Tạo tác giả mới |
| `GET` | `/api/authors/{id}/` | Chi tiết tác giả |
| `PUT` | `/api/authors/{id}/` | Cập nhật tác giả |
| `DELETE` | `/api/authors/{id}/` | Xóa tác giả |

**Response**:
```json
[
  {"id": 1, "name": "Nguyễn Nhật Ánh", "bio": "Nhà văn Việt Nam nổi tiếng...", "nationality": "Việt Nam"},
  {"id": 2, "name": "Dale Carnegie", "bio": "Tác giả Mỹ nổi tiếng...", "nationality": "Mỹ"},
  {"id": 3, "name": "Robert C. Martin", "bio": "Kỹ sư phần mềm...", "nationality": "Mỹ"}
]
```

### 4.3. Publishers

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/publishers/` | Lấy danh sách nhà xuất bản |
| `POST` | `/api/publishers/` | Tạo NXB mới |
| `GET` | `/api/publishers/{id}/` | Chi tiết NXB |
| `PUT` | `/api/publishers/{id}/` | Cập nhật NXB |
| `DELETE` | `/api/publishers/{id}/` | Xóa NXB |

---

## 5. Customer Service API (Port 8003)

**Base URL**: `http://localhost:8003/api/`  
**Database**: `customer_db` (MySQL)  
**Authentication**: JWT (HS256, hết hạn 24 giờ)

### 5.1. Authentication

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `POST` | `/api/register/` | Đăng ký tài khoản |
| `POST` | `/api/login/` | Đăng nhập, nhận JWT token |
| `POST` | `/api/logout/` | Đăng xuất |

**Request**: `POST /api/register/`
```json
{
  "name": "Nguyễn Văn A",
  "email": "nguyenvana@email.com",
  "phone": "0901234567",
  "password": "matkhau123"
}
```

**Response**:
```json
{
  "message": "Đăng ký thành công",
  "customer": {
    "id": 1,
    "name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com",
    "phone": "0901234567"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Request**: `POST /api/login/`
```json
{
  "email": "nguyenvana@email.com",
  "password": "matkhau123"
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "customer": {
    "id": 1,
    "name": "Nguyễn Văn A",
    "email": "nguyenvana@email.com"
  }
}
```

### 5.2. Customer Profile

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/profile/` | Lấy thông tin cá nhân |
| `PUT` | `/api/profile/` | Cập nhật thông tin cá nhân |

### 5.3. Delivery Addresses

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/addresses/` | Danh sách địa chỉ giao hàng |
| `POST` | `/api/addresses/` | Thêm địa chỉ mới |
| `GET` | `/api/addresses/{id}/` | Chi tiết địa chỉ |
| `PUT` | `/api/addresses/{id}/` | Cập nhật địa chỉ |
| `DELETE` | `/api/addresses/{id}/` | Xóa địa chỉ |

**Request**: `POST /api/addresses/`
```json
{
  "name": "Nguyễn Văn A",
  "phone": "0901234567",
  "address": "123 Nguyễn Văn Linh",
  "city": "TP.HCM",
  "district": "Quận 7",
  "ward": "Phường Tân Phong",
  "is_default": true
}
```

---

## 6. Order Service API (Port 8007)

**Base URL**: `http://localhost:8007/api/`  
**Database**: `order_db` (MySQL)  
**Giao tiếp**: Book Service (cập nhật tồn kho), Cart Service (tắt giỏ hàng), Pay Service (tạo thanh toán), Ship Service (tạo vận chuyển)

### 6.1. Orders

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/orders/` | Danh sách đơn hàng (`?customer_id=N`, `?status=pending`) |
| `POST` | `/api/orders/` | Tạo đơn hàng mới |
| `GET` | `/api/orders/{id}/` | Chi tiết đơn hàng |
| `PUT` | `/api/orders/{id}/` | Cập nhật đơn hàng |
| `PATCH` | `/api/orders/{id}/status/` | Cập nhật trạng thái đơn hàng |

**Request**: `POST /api/orders/`
```json
{
  "customer_id": 1,
  "cart_id": 1,
  "shipping_address": "123 Nguyễn Văn Linh, Q7, TP.HCM",
  "shipping_method_id": 1,
  "payment_method_id": 1,
  "notes": "Giao giờ hành chính"
}
```

**Response**:
```json
{
  "id": 1,
  "order_number": "ORD-20260310-001",
  "customer_id": 1,
  "shipping_address": "123 Nguyễn Văn Linh, Q7, TP.HCM",
  "shipping_method_id": 1,
  "payment_method_id": 1,
  "subtotal": "255000",
  "shipping_fee": "25000",
  "discount": "0",
  "total": "280000",
  "status": "pending",
  "items": [
    {"book_id": 1, "book_title": "Cho tôi xin một vé đi tuổi thơ", "quantity": 1, "price": "85000"},
    {"book_id": 4, "book_title": "Đắc nhân tâm", "quantity": 1, "price": "120000"}
  ],
  "notes": "Giao giờ hành chính",
  "created_at": "2026-03-10T09:30:00Z"
}
```

**Trạng thái đơn hàng**: `pending` → `confirmed` → `processing` → `shipped` → `delivered` | `cancelled`

### 6.2. Order Items

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/orders/{id}/items/` | Danh sách sản phẩm trong đơn |

---

## 7. Pay Service API (Port 8009)

**Base URL**: `http://localhost:8009/api/`  
**Database**: `pay_db` (MySQL)

### 7.1. Payment Methods

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/methods/` | Danh sách phương thức thanh toán |
| `GET` | `/api/methods/{id}/` | Chi tiết phương thức |

**Response**:
```json
[
  {"id": 1, "name": "Thanh toán khi nhận hàng (COD)", "code": "cod", "is_active": true},
  {"id": 2, "name": "Chuyển khoản ngân hàng", "code": "bank", "is_active": true},
  {"id": 3, "name": "Ví MoMo", "code": "momo", "is_active": true},
  {"id": 4, "name": "VNPay", "code": "vnpay", "is_active": true}
]
```

### 7.2. Payments

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/payments/` | Danh sách thanh toán (`?order_id=N`) |
| `POST` | `/api/payments/` | Tạo thanh toán cho đơn hàng |
| `GET` | `/api/payments/{id}/` | Chi tiết thanh toán |
| `POST` | `/api/payments/{id}/process/` | Xử lý thanh toán |

**Request**: `POST /api/payments/`
```json
{
  "order_id": 1,
  "payment_method_id": 1,
  "amount": "280000"
}
```

**Response**:
```json
{
  "id": 1,
  "order_id": 1,
  "payment_method_id": 1,
  "amount": "280000",
  "status": "pending",
  "transaction_id": null,
  "paid_at": null,
  "created_at": "2026-03-10T09:30:00Z"
}
```

**Request**: `POST /api/payments/{id}/process/`

**Response**:
```json
{
  "id": 1,
  "status": "completed",
  "transaction_id": "TXN-a1b2c3d4e5f6",
  "paid_at": "2026-03-10T09:35:00Z"
}
```

**Trạng thái thanh toán**: `pending` → `completed` | `failed` | `refunded`

---

## 8. Ship Service API (Port 8008)

**Base URL**: `http://localhost:8008/api/`  
**Database**: `ship_db` (MySQL)

### 8.1. Shipping Methods

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/methods/` | Danh sách phương thức vận chuyển |
| `GET` | `/api/methods/{id}/` | Chi tiết phương thức |

**Response**:
```json
[
  {"id": 1, "name": "Giao hàng tiêu chuẩn", "fee": "25000", "estimated_days": "3-5 ngày", "is_active": true},
  {"id": 2, "name": "Giao hàng nhanh", "fee": "45000", "estimated_days": "1-2 ngày", "is_active": true},
  {"id": 3, "name": "Giao hàng hỏa tốc", "fee": "70000", "estimated_days": "Trong ngày", "is_active": true}
]
```

### 8.2. Shipments

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/shipments/` | Danh sách vận đơn (`?order_id=N`, `?status=pending`) |
| `POST` | `/api/shipments/` | Tạo vận đơn |
| `GET` | `/api/shipments/{id}/` | Chi tiết vận đơn |
| `PATCH` | `/api/shipments/{id}/status/` | Cập nhật trạng thái vận đơn |

**Request**: `POST /api/shipments/`
```json
{
  "order_id": 1,
  "carrier": "GHTK",
  "tracking_number": "GHTK123456789"
}
```

**Response**:
```json
{
  "id": 1,
  "order_id": 1,
  "tracking_number": "GHTK123456789",
  "carrier": "GHTK",
  "status": "pending",
  "shipped_at": null,
  "delivered_at": null,
  "created_at": "2026-03-10T09:30:00Z"
}
```

**Trạng thái vận chuyển**: `pending` → `shipped` → `in_transit` → `delivered` | `returned`

---

## 9. Comment-Rate Service API (Port 8010)

**Base URL**: `http://localhost:8010/api/`  
**Database**: `comment_db` (MySQL)  
**Giao tiếp**: Gọi Book Service để cập nhật điểm đánh giá trung bình

### 9.1. Reviews

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/reviews/` | Danh sách đánh giá (`?book_id=N`, `?customer_id=N`) |
| `POST` | `/api/reviews/` | Viết đánh giá mới |
| `GET` | `/api/reviews/{id}/` | Chi tiết đánh giá |
| `PUT` | `/api/reviews/{id}/` | Cập nhật đánh giá |
| `DELETE` | `/api/reviews/{id}/` | Xóa đánh giá |

**Request**: `POST /api/reviews/`
```json
{
  "book_id": 1,
  "customer_id": 1,
  "rating": 5,
  "title": "Sách rất hay!",
  "content": "Một tác phẩm tuyệt vời về tuổi thơ, rất đáng đọc."
}
```

**Response**:
```json
{
  "id": 1,
  "book_id": 1,
  "customer_id": 1,
  "rating": 5,
  "title": "Sách rất hay!",
  "content": "Một tác phẩm tuyệt vời về tuổi thơ, rất đáng đọc.",
  "is_approved": false,
  "created_at": "2026-03-10T10:00:00Z"
}
```

> **Lưu ý**: `is_approved` mặc định là `false`, cần staff phê duyệt. Rating từ 1 đến 5.

---

## 10. Recommender AI Service API (Port 8011)

**Base URL**: `http://localhost:8011/api/`  
**Database**: `recommender_db` (MySQL)  
**Thư viện ML**: numpy, scikit-learn

### 10.1. Recommendations

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/recommendations/` | Gợi ý cho khách hàng (`?customer_id=N`) |
| `GET` | `/api/trending/` | Sách đang thịnh hành |
| `GET` | `/api/best-rated/` | Sách được đánh giá cao nhất |
| `GET` | `/api/similar/{book_id}/` | Sách tương tự |

**Response** (`GET /api/recommendations/?customer_id=1`):
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "book_id": 8,
    "score": "0.9200",
    "reason": "Dựa trên lịch sử mua hàng và sở thích thể loại Văn học"
  }
]
```

---

## 11. Staff Service API (Port 8001)

**Base URL**: `http://localhost:8001/api/`  
**Database**: `staff_db` (MySQL)  
**Authentication**: JWT (HS256)

### 11.1. Authentication

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `POST` | `/api/login/` | Đăng nhập staff |
| `POST` | `/api/logout/` | Đăng xuất staff |

**Request**: `POST /api/login/`
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "staff": {
    "id": 1,
    "username": "admin",
    "name": "Administrator",
    "email": "admin@bookhaven.vn",
    "role": "admin"
  }
}
```

### 11.2. Staff Management

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/staff/` | Danh sách nhân viên |
| `POST` | `/api/staff/` | Tạo nhân viên mới |
| `GET` | `/api/staff/{id}/` | Chi tiết nhân viên |
| `PUT` | `/api/staff/{id}/` | Cập nhật nhân viên |
| `DELETE` | `/api/staff/{id}/` | Xóa nhân viên |

### 11.3. Inventory Logs

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/inventory-logs/` | Lịch sử thao tác kho (`?staff_id=N`, `?book_id=N`) |
| `POST` | `/api/inventory-logs/` | Ghi log thao tác kho |

**Response**:
```json
{
  "id": 1,
  "staff_id": 1,
  "book_id": 1,
  "action": "import",
  "quantity": 50,
  "notes": "Nhập hàng đợt 1",
  "created_at": "2026-03-10T08:00:00Z"
}
```

---

## 12. Manager Service API (Port 8002)

**Base URL**: `http://localhost:8002/api/`  
**Database**: `manager_db` (MySQL)  
**Authentication**: JWT (HS256)

### 12.1. Authentication

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `POST` | `/api/login/` | Đăng nhập manager |
| `POST` | `/api/logout/` | Đăng xuất |

### 12.2. Dashboard & Reports

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/dashboard/` | Tổng quan thống kê (doanh thu, đơn hàng, khách hàng) |
| `GET` | `/api/reports/sales/` | Báo cáo doanh thu |
| `GET` | `/api/reports/inventory/` | Báo cáo tồn kho |

---

## 13. Mã lỗi chung

| HTTP Status | Ý nghĩa | Ví dụ |
|-------------|----------|-------|
| `200` | Thành công | GET, PUT, PATCH thành công |
| `201` | Tạo thành công | POST tạo mới thành công |
| `204` | Xóa thành công | DELETE thành công |
| `400` | Yêu cầu không hợp lệ | Thiếu field bắt buộc, validation lỗi |
| `401` | Chưa xác thực | Token không hợp lệ hoặc hết hạn |
| `403` | Không có quyền | Staff truy cập API manager |
| `404` | Không tìm thấy | ID không tồn tại |
| `500` | Lỗi server | Lỗi hệ thống nội bộ |

**Định dạng lỗi**:
```json
{
  "error": "Mô tả lỗi ngắn gọn",
  "detail": "Chi tiết lỗi (nếu có)"
}
```

**Validation Error**:
```json
{
  "field_name": ["Thông báo lỗi validation."],
  "quantity": ["Ensure this value is greater than or equal to 1."]
}
```

---

## Phụ lục: Tài khoản test

| Vai trò | Username/Email | Mật khẩu |
|---------|---------------|-----------|
| Customer | customer1 | pass123 |
| Admin | admin@bookstore.com | admin123 |
| Staff | staff1@bookstore.com | staff123 |
| Manager | manager1@bookstore.com | manager123 |
