-- =====================================================
-- SQL Script for Monolithic Bookstore Database
-- Database: bookstore_monolith
-- Comprehensive schema with all domain entities
-- =====================================================

-- Create database
CREATE DATABASE IF NOT EXISTS bookstore_monolith CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore_monolith;

-- =====================================================
-- CUSTOMER DOMAIN
-- =====================================================

-- User Roles
CREATE TABLE IF NOT EXISTS store_userrole (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL,
    permissions JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Status
CREATE TABLE IF NOT EXISTS store_userstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customers (Main User Table)
CREATE TABLE IF NOT EXISTS store_customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(20) NULL,
    address TEXT NULL,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Profiles
CREATE TABLE IF NOT EXISTS store_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    avatar_url VARCHAR(500) NULL,
    bio TEXT NULL,
    preferences JSON NULL,
    notification_settings JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Login Sessions
CREATE TABLE IF NOT EXISTS store_loginsession (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    device_info VARCHAR(255) NULL,
    ip_address VARCHAR(45) NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    INDEX idx_user_session (user_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- BOOK DOMAIN
-- =====================================================

-- Publishers
CREATE TABLE IF NOT EXISTS store_publisher (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NULL,
    contact_email VARCHAR(254) NULL,
    phone VARCHAR(20) NULL,
    website VARCHAR(200) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Authors
CREATE TABLE IF NOT EXISTS store_author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    biography TEXT NULL,
    photo_url VARCHAR(500) NULL,
    nationality VARCHAR(100) NULL,
    birth_date DATE NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Categories
CREATE TABLE IF NOT EXISTS store_category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    parent_id INT NULL,
    icon VARCHAR(50) NULL,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES store_category(category_id) ON DELETE SET NULL,
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book Status
CREATE TABLE IF NOT EXISTS store_bookstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Books
CREATE TABLE IF NOT EXISTS store_book (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    publisher_id INT NULL,
    category_id INT NULL,
    price DECIMAL(12, 2) NOT NULL,
    stock_quantity INT UNSIGNED DEFAULT 0,
    publication_date DATE NULL,
    short_description TEXT NULL,
    status_id INT NULL,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES store_author(author_id) ON DELETE RESTRICT,
    FOREIGN KEY (publisher_id) REFERENCES store_publisher(publisher_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES store_category(category_id) ON DELETE SET NULL,
    FOREIGN KEY (status_id) REFERENCES store_bookstatus(id) ON DELETE SET NULL,
    INDEX idx_title (title),
    INDEX idx_author (author_id),
    INDEX idx_category (category_id),
    INDEX idx_price (price),
    INDEX idx_rating (average_rating DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book Images
CREATE TABLE IF NOT EXISTS store_bookimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    INDEX idx_book (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book Descriptions
CREATE TABLE IF NOT EXISTS store_bookdescription (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL UNIQUE,
    full_description TEXT NULL,
    table_of_contents TEXT NULL,
    about_author TEXT NULL,
    format_info TEXT NULL,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book Tags
CREATE TABLE IF NOT EXISTS store_booktag (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book-Tag Association
CREATE TABLE IF NOT EXISTS store_book_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    booktag_id INT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    FOREIGN KEY (booktag_id) REFERENCES store_booktag(id) ON DELETE CASCADE,
    UNIQUE KEY unique_book_tag (book_id, booktag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book Inventory
CREATE TABLE IF NOT EXISTS store_bookinventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL UNIQUE,
    quantity INT DEFAULT 0,
    reserved_quantity INT DEFAULT 0,
    min_stock_level INT DEFAULT 5,
    max_stock_level INT DEFAULT 100,
    reorder_point INT DEFAULT 10,
    last_restocked DATETIME NULL,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- CART DOMAIN
-- =====================================================

-- Cart Status
CREATE TABLE IF NOT EXISTS store_cartstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Carts
CREATE TABLE IF NOT EXISTS store_cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    status_id INT NULL,
    total_price DECIMAL(12, 2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES store_cartstatus(id) ON DELETE SET NULL,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart Items
CREATE TABLE IF NOT EXISTS store_cartitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT UNSIGNED DEFAULT 1,
    unit_price DECIMAL(12, 2) NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES store_cart(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_book (cart_id, book_id),
    INDEX idx_cart (cart_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Saved Carts
CREATE TABLE IF NOT EXISTS store_savedcart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    customer_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES store_cart(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart History
CREATE TABLE IF NOT EXISTS store_carthistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    details JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES store_cart(cart_id) ON DELETE CASCADE,
    INDEX idx_cart (cart_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- ORDER DOMAIN
-- =====================================================

-- Order Status
CREATE TABLE IF NOT EXISTS store_orderstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL,
    display_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Orders
CREATE TABLE IF NOT EXISTS store_order (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    status_id INT NULL,
    total_price DECIMAL(12, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(12, 2) DEFAULT 0.00,
    shipping_fee DECIMAL(12, 2) DEFAULT 0.00,
    discount_amount DECIMAL(12, 2) DEFAULT 0.00,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT NULL,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES store_orderstatus(id) ON DELETE SET NULL,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status_id),
    INDEX idx_order_number (order_number),
    INDEX idx_order_date (order_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order Items
CREATE TABLE IF NOT EXISTS store_orderitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE RESTRICT,
    INDEX idx_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order History
CREATE TABLE IF NOT EXISTS store_orderhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status_id INT NULL,
    changed_by_id INT NULL,
    notes TEXT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES store_orderstatus(id) ON DELETE SET NULL,
    FOREIGN KEY (changed_by_id) REFERENCES store_customer(customer_id) ON DELETE SET NULL,
    INDEX idx_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order Tracking
CREATE TABLE IF NOT EXISTS store_ordertracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status VARCHAR(100) NOT NULL,
    location VARCHAR(255) NULL,
    description TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    INDEX idx_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order Cancellations
CREATE TABLE IF NOT EXISTS store_ordercancellation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    reason TEXT NOT NULL,
    cancelled_by_id INT NULL,
    refund_amount DECIMAL(12, 2) DEFAULT 0.00,
    cancelled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (cancelled_by_id) REFERENCES store_customer(customer_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Invoices
CREATE TABLE IF NOT EXISTS store_invoice (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(20) UNIQUE NOT NULL,
    order_id INT NOT NULL UNIQUE,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    notes TEXT NULL,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order Notes
CREATE TABLE IF NOT EXISTS store_ordernote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    created_by_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES store_customer(customer_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- PAYMENT DOMAIN
-- =====================================================

-- Payment Methods
CREATE TABLE IF NOT EXISTS store_paymentmethod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NULL,
    icon VARCHAR(50) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payment Status
CREATE TABLE IF NOT EXISTS store_paymentstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payments
CREATE TABLE IF NOT EXISTS store_payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    method_id INT NOT NULL,
    status_id INT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    transaction_id VARCHAR(100) NULL,
    payment_date DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (method_id) REFERENCES store_paymentmethod(id) ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES store_paymentstatus(id) ON DELETE SET NULL,
    INDEX idx_order (order_id),
    INDEX idx_transaction (transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transactions
CREATE TABLE IF NOT EXISTS store_transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    gateway_response JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES store_payment(payment_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Refunds
CREATE TABLE IF NOT EXISTS store_refund (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    reason TEXT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    processed_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES store_payment(payment_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- SHIPPING DOMAIN
-- =====================================================

-- Shipping Methods
CREATE TABLE IF NOT EXISTS store_shippingmethod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NULL,
    base_cost DECIMAL(12, 2) DEFAULT 0.00,
    estimated_days INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Shipping Status
CREATE TABLE IF NOT EXISTS store_shippingstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Delivery Addresses
CREATE TABLE IF NOT EXISTS store_deliveryaddress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    recipient_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100) NULL,
    district VARCHAR(100) NULL,
    ward VARCHAR(100) NULL,
    detail TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    INDEX idx_customer (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Shipping
CREATE TABLE IF NOT EXISTS store_shipping (
    shipping_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    method_id INT NOT NULL,
    status_id INT NULL,
    delivery_address_id INT NULL,
    tracking_number VARCHAR(100) NULL,
    shipping_cost DECIMAL(12, 2) DEFAULT 0.00,
    estimated_delivery DATE NULL,
    actual_delivery DATETIME NULL,
    shipped_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES store_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (method_id) REFERENCES store_shippingmethod(id) ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES store_shippingstatus(id) ON DELETE SET NULL,
    FOREIGN KEY (delivery_address_id) REFERENCES store_deliveryaddress(id) ON DELETE SET NULL,
    INDEX idx_tracking (tracking_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Delivery Tracking
CREATE TABLE IF NOT EXISTS store_deliverytracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shipping_id INT NOT NULL,
    status VARCHAR(100) NOT NULL,
    location VARCHAR(255) NULL,
    description TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipping_id) REFERENCES store_shipping(shipping_id) ON DELETE CASCADE,
    INDEX idx_shipping (shipping_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- REVIEW DOMAIN
-- =====================================================

-- Ratings
CREATE TABLE IF NOT EXISTS store_rating (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    customer_id INT NOT NULL,
    score INT NOT NULL CHECK (score >= 1 AND score <= 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    UNIQUE KEY unique_book_customer (book_id, customer_id),
    INDEX idx_book (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reviews
CREATE TABLE IF NOT EXISTS store_review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rating_id INT NOT NULL UNIQUE,
    title VARCHAR(255) NULL,
    content TEXT NOT NULL,
    pros TEXT NULL,
    cons TEXT NULL,
    is_recommended BOOLEAN DEFAULT TRUE,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rating_id) REFERENCES store_rating(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Behavior (for recommendations)
CREATE TABLE IF NOT EXISTS store_userbehavior (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    book_id INT NOT NULL,
    view_count INT DEFAULT 0,
    add_to_cart_count INT DEFAULT 0,
    purchase_count INT DEFAULT 0,
    last_viewed DATETIME NULL,
    last_purchased DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    UNIQUE KEY unique_customer_book (customer_id, book_id),
    INDEX idx_customer (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Purchase History
CREATE TABLE IF NOT EXISTS store_purchasehistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    purchase_price DECIMAL(12, 2) NOT NULL,
    purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    INDEX idx_customer (customer_id),
    INDEX idx_book (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recommendation Rules
CREATE TABLE IF NOT EXISTS store_recommendationrule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    parameters JSON NULL,
    weight DECIMAL(3, 2) DEFAULT 1.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recommendations
CREATE TABLE IF NOT EXISTS store_recommendation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    book_id INT NOT NULL,
    score DECIMAL(5, 4) NOT NULL,
    reason VARCHAR(255) NULL,
    rule_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    FOREIGN KEY (rule_id) REFERENCES store_recommendationrule(id) ON DELETE SET NULL,
    INDEX idx_customer (customer_id),
    INDEX idx_score (score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- STAFF DOMAIN
-- =====================================================

-- Staff
CREATE TABLE IF NOT EXISTS store_staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(20) NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'Staff',
    is_active BOOLEAN DEFAULT TRUE,
    hire_date DATE NULL,
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admin (extends Staff)
CREATE TABLE IF NOT EXISTS store_admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL UNIQUE,
    admin_level INT DEFAULT 1,
    permissions JSON NULL,
    FOREIGN KEY (staff_id) REFERENCES store_staff(staff_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inventory Logs
CREATE TABLE IF NOT EXISTS store_inventorylog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    staff_id INT NULL,
    change_type VARCHAR(50) NOT NULL,
    quantity_change INT NOT NULL,
    previous_quantity INT NOT NULL,
    new_quantity INT NOT NULL,
    cost_price DECIMAL(12, 2) NULL,
    supplier VARCHAR(255) NULL,
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES store_book(book_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES store_staff(staff_id) ON DELETE SET NULL,
    INDEX idx_book (book_id),
    INDEX idx_staff (staff_id),
    INDEX idx_date (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admin Action Logs
CREATE TABLE IF NOT EXISTS store_adminactionlog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NULL,
    entity_id INT NULL,
    details JSON NULL,
    ip_address VARCHAR(45) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES store_admin(id) ON DELETE CASCADE,
    INDEX idx_admin (admin_id),
    INDEX idx_date (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert Order Status
INSERT INTO store_orderstatus (name, description, display_order) VALUES
('Pending', 'Đơn hàng mới, chờ xác nhận', 1),
('Processing', 'Đang xử lý', 2),
('Shipped', 'Đã giao cho vận chuyển', 3),
('Delivered', 'Đã giao hàng', 4),
('Cancelled', 'Đã hủy', 5),
('Refunded', 'Đã hoàn tiền', 6);

-- Insert Cart Status
INSERT INTO store_cartstatus (name, description) VALUES
('Active', 'Giỏ hàng đang hoạt động'),
('Saved', 'Giỏ hàng đã lưu'),
('Converted', 'Đã chuyển thành đơn hàng'),
('Abandoned', 'Giỏ hàng bị bỏ rơi');

-- Insert Book Status
INSERT INTO store_bookstatus (name, description) VALUES
('Available', 'Còn hàng'),
('OutOfStock', 'Hết hàng'),
('ComingSoon', 'Sắp ra mắt'),
('Discontinued', 'Ngừng kinh doanh');

-- Insert Payment Methods
INSERT INTO store_paymentmethod (name, code, description, icon, display_order) VALUES
('Tiền mặt (COD)', 'cod', 'Thanh toán khi nhận hàng', '💵', 1),
('Chuyển khoản ngân hàng', 'bank_transfer', 'Chuyển khoản qua ngân hàng', '🏦', 2),
('Ví điện tử MoMo', 'momo', 'Thanh toán qua ví MoMo', '📱', 3),
('Ví điện tử ZaloPay', 'zalopay', 'Thanh toán qua ZaloPay', '💳', 4),
('VNPay', 'vnpay', 'Thanh toán qua VNPay', '💳', 5),
('Thẻ tín dụng/ghi nợ', 'card', 'Visa, Mastercard, JCB', '💳', 6);

-- Insert Payment Status
INSERT INTO store_paymentstatus (name, description) VALUES
('Pending', 'Chờ thanh toán'),
('Processing', 'Đang xử lý'),
('Completed', 'Đã thanh toán'),
('Failed', 'Thất bại'),
('Refunded', 'Đã hoàn tiền');

-- Insert Shipping Methods
INSERT INTO store_shippingmethod (name, code, description, base_cost, estimated_days, display_order) VALUES
('Giao hàng tiêu chuẩn', 'standard', 'Giao hàng trong 3-5 ngày', 25000, 5, 1),
('Giao hàng nhanh', 'express', 'Giao hàng trong 1-2 ngày', 45000, 2, 2),
('Giao hàng hỏa tốc', 'same_day', 'Giao trong ngày (nội thành)', 65000, 1, 3),
('Miễn phí vận chuyển', 'free', 'Đơn hàng từ 500k (3-7 ngày)', 0, 7, 4);

-- Insert Shipping Status
INSERT INTO store_shippingstatus (name, description) VALUES
('Pending', 'Chờ lấy hàng'),
('PickedUp', 'Đã lấy hàng'),
('InTransit', 'Đang vận chuyển'),
('OutForDelivery', 'Đang giao'),
('Delivered', 'Đã giao'),
('Failed', 'Giao thất bại'),
('Returned', 'Đã trả về');

-- Insert User Roles
INSERT INTO store_userrole (name, description) VALUES
('Customer', 'Khách hàng thông thường'),
('VIP', 'Khách hàng VIP'),
('Staff', 'Nhân viên'),
('Admin', 'Quản trị viên');

-- Insert User Status
INSERT INTO store_userstatus (name, description) VALUES
('Active', 'Hoạt động'),
('Inactive', 'Không hoạt động'),
('Suspended', 'Tạm khóa'),
('Banned', 'Cấm vĩnh viễn');

-- Insert Categories
INSERT INTO store_category (name, description, icon) VALUES
('Văn học', 'Tiểu thuyết, truyện ngắn, thơ', '📚'),
('Kinh tế', 'Sách kinh doanh, tài chính', '💼'),
('Khoa học', 'Sách khoa học tự nhiên', '🔬'),
('Công nghệ', 'Sách IT, lập trình', '💻'),
('Thiếu nhi', 'Sách cho trẻ em', '🧒'),
('Tâm lý - Kỹ năng sống', 'Self-help, phát triển bản thân', '🧠'),
('Ngoại ngữ', 'Sách học tiếng Anh, tiếng Nhật...', '🌍'),
('Lịch sử', 'Sách lịch sử Việt Nam và thế giới', '📜');

-- Insert Sample Authors
INSERT INTO store_author (name, biography, nationality) VALUES
('Nguyễn Nhật Ánh', 'Nhà văn nổi tiếng với các tác phẩm văn học thiếu nhi', 'Việt Nam'),
('Paulo Coelho', 'Tiểu thuyết gia người Brazil', 'Brazil'),
('Dale Carnegie', 'Tác giả sách self-help nổi tiếng', 'Mỹ'),
('Robert C. Martin', 'Tác giả Clean Code, chuyên gia phần mềm', 'Mỹ'),
('J.K. Rowling', 'Tác giả series Harry Potter', 'Anh'),
('Haruki Murakami', 'Tiểu thuyết gia Nhật Bản nổi tiếng', 'Nhật Bản');

-- Insert Sample Publisher
INSERT INTO store_publisher (name, contact_email, website) VALUES
('NXB Trẻ', 'contact@nxbtre.com.vn', 'https://nxbtre.com.vn'),
('NXB Kim Đồng', 'contact@nxbkimdong.com.vn', 'https://nxbkimdong.com.vn'),
('NXB Tổng Hợp TPHCM', 'contact@nxbhcm.com.vn', 'https://nxbhcm.com.vn'),
('OReilly Media', 'contact@oreilly.com', 'https://oreilly.com');

-- Insert Sample Books
INSERT INTO store_book (isbn, title, author_id, publisher_id, category_id, price, stock_quantity, short_description) VALUES
('978-604-1-00001-1', 'Mắt Biếc', 1, 1, 1, 85000, 100, 'Câu chuyện tình yêu đầy cảm xúc của Nguyễn Nhật Ánh'),
('978-604-1-00002-2', 'Nhà Giả Kim', 2, 1, 1, 79000, 80, 'Tiểu thuyết best-seller của Paulo Coelho'),
('978-604-1-00003-3', 'Đắc Nhân Tâm', 3, 2, 6, 86000, 150, 'Nghệ thuật giao tiếp và ứng xử'),
('978-604-1-00004-4', 'Clean Code', 4, 4, 4, 450000, 30, 'Cẩm nang viết code sạch cho lập trình viên'),
('978-604-1-00005-5', 'Harry Potter và Hòn Đá Phù Thủy', 5, 2, 5, 150000, 120, 'Cuốn đầu tiên trong series Harry Potter'),
('978-604-1-00006-6', 'Kafka Bên Bờ Biển', 6, 1, 1, 165000, 45, 'Tiểu thuyết huyền bí của Murakami'),
('978-604-1-00007-7', 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh', 1, 1, 1, 75000, 90, 'Tuổi thơ và những kỷ niệm đẹp'),
('978-604-1-00008-8', 'Rừng Na-uy', 6, 1, 1, 145000, 60, 'Tiểu thuyết lãng mạn của Murakami'),
('978-604-1-00009-9', 'Quẳng Gánh Lo Đi Và Vui Sống', 3, 2, 6, 95000, 70, 'Bí quyết sống vui vẻ và hạnh phúc'),
('978-604-1-00010-0', 'The Pragmatic Programmer', 4, 4, 4, 520000, 25, 'Sách kinh điển cho lập trình viên');

-- Insert Sample Staff
INSERT INTO store_staff (name, email, phone, password, role) VALUES
('Admin System', 'admin@bookstore.com', '0901234567', 'pbkdf2_sha256$720000$admin$hash', 'Admin'),
('Nhân viên 1', 'staff1@bookstore.com', '0901234568', 'pbkdf2_sha256$720000$staff1$hash', 'Staff'),
('Nhân viên 2', 'staff2@bookstore.com', '0901234569', 'pbkdf2_sha256$720000$staff2$hash', 'Staff');

-- Insert Recommendation Rules
INSERT INTO store_recommendationrule (name, rule_type, parameters, weight) VALUES
('Cùng tác giả', 'same_author', '{"boost": 1.5}', 1.00),
('Cùng danh mục', 'same_category', '{"boost": 1.2}', 0.80),
('Khách hàng cũng mua', 'collaborative', '{"min_users": 5}', 1.20),
('Sách bán chạy', 'popularity', '{"days": 30}', 0.70),
('Đánh giá cao', 'top_rated', '{"min_rating": 4.0}', 0.90);

-- =====================================================
-- VIEWS
-- =====================================================

-- View: Book with full info
CREATE OR REPLACE VIEW v_book_full AS
SELECT 
    b.book_id,
    b.isbn,
    b.title,
    a.name as author_name,
    p.name as publisher_name,
    c.name as category_name,
    b.price,
    b.stock_quantity,
    b.average_rating,
    b.rating_count,
    bs.name as status_name
FROM store_book b
LEFT JOIN store_author a ON b.author_id = a.author_id
LEFT JOIN store_publisher p ON b.publisher_id = p.publisher_id
LEFT JOIN store_category c ON b.category_id = c.category_id
LEFT JOIN store_bookstatus bs ON b.status_id = bs.id;

-- View: Order summary
CREATE OR REPLACE VIEW v_order_summary AS
SELECT 
    o.order_id,
    o.order_number,
    c.name as customer_name,
    c.email as customer_email,
    os.name as status_name,
    o.total_price,
    o.order_date,
    COUNT(oi.id) as item_count
FROM store_order o
JOIN store_customer c ON o.customer_id = c.customer_id
LEFT JOIN store_orderstatus os ON o.status_id = os.id
LEFT JOIN store_orderitem oi ON o.order_id = oi.order_id
GROUP BY o.order_id;

-- =====================================================
-- TRIGGERS
-- =====================================================

DELIMITER //

-- Trigger: Update book average rating after rating insert/update
CREATE TRIGGER trg_update_book_rating_insert
AFTER INSERT ON store_rating
FOR EACH ROW
BEGIN
    UPDATE store_book 
    SET 
        average_rating = (SELECT AVG(score) FROM store_rating WHERE book_id = NEW.book_id),
        rating_count = (SELECT COUNT(*) FROM store_rating WHERE book_id = NEW.book_id)
    WHERE book_id = NEW.book_id;
END//

CREATE TRIGGER trg_update_book_rating_update
AFTER UPDATE ON store_rating
FOR EACH ROW
BEGIN
    UPDATE store_book 
    SET 
        average_rating = (SELECT AVG(score) FROM store_rating WHERE book_id = NEW.book_id),
        rating_count = (SELECT COUNT(*) FROM store_rating WHERE book_id = NEW.book_id)
    WHERE book_id = NEW.book_id;
END//

-- Trigger: Auto-generate order number
CREATE TRIGGER trg_generate_order_number
BEFORE INSERT ON store_order
FOR EACH ROW
BEGIN
    IF NEW.order_number IS NULL OR NEW.order_number = '' THEN
        SET NEW.order_number = CONCAT('ORD', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(FLOOR(RAND() * 10000), 4, '0'));
    END IF;
END//

DELIMITER ;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Full-text search on books
ALTER TABLE store_book ADD FULLTEXT INDEX ft_book_search (title, short_description);

-- =====================================================
-- END OF SCRIPT
-- =====================================================
