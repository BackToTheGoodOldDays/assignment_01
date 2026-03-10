-- =====================================================
-- BookStore Microservices - Database Initialization
-- =====================================================
-- This script creates all databases and sample data

-- =====================================================
-- STAFF DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS staff_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE staff_db;

CREATE TABLE IF NOT EXISTS staff_staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff_inventorylog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    book_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff_staff(id)
);

-- Insert default admin (password: admin123 - SHA256 hashed)
INSERT IGNORE INTO staff_staff (username, name, email, password, role)
VALUES ('admin', 'Administrator', 'admin@bookhaven.vn', 
        '240be518fabd2724ddb6f04eeb9d44f7e4c9e5e2d4e91d4e9f8f7e4c9e5e2d4e', 'admin');

-- =====================================================
-- CATALOG DATABASE  
-- =====================================================
CREATE DATABASE IF NOT EXISTS catalog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE catalog_db;

CREATE TABLE IF NOT EXISTS catalog_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS catalog_author (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bio TEXT,
    nationality VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS catalog_publisher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample categories
INSERT IGNORE INTO catalog_category (id, name, description) VALUES 
(1, 'Văn học', 'Sách văn học Việt Nam và thế giới'),
(2, 'Kinh tế', 'Sách kinh tế, kinh doanh, quản trị'),
(3, 'Công nghệ', 'Sách lập trình, IT, khoa học máy tính'),
(4, 'Tâm lý', 'Sách tâm lý học, phát triển bản thân'),
(5, 'Thiếu nhi', 'Sách dành cho trẻ em');

-- Insert sample authors
INSERT IGNORE INTO catalog_author (id, name, bio, nationality) VALUES
(1, 'Nguyễn Nhật Ánh', 'Nhà văn Việt Nam nổi tiếng với các tác phẩm về tuổi thơ', 'Việt Nam'),
(2, 'Dale Carnegie', 'Tác giả Mỹ nổi tiếng với sách kỹ năng sống', 'Mỹ'),
(3, 'Robert C. Martin', 'Kỹ sư phần mềm, tác giả Clean Code', 'Mỹ'),
(4, 'Paulo Coelho', 'Nhà văn Brazil, tác giả Nhà giả kim', 'Brazil'),
(5, 'Haruki Murakami', 'Nhà văn Nhật Bản nổi tiếng', 'Nhật Bản');

-- =====================================================
-- BOOK DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS book_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE book_db;

CREATE TABLE IF NOT EXISTS books_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT,
    category_id INT,
    price DECIMAL(12, 0) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    isbn VARCHAR(20),
    pages INT,
    publisher_id INT,
    published_year INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books_bookimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (book_id) REFERENCES books_book(id) ON DELETE CASCADE
);

-- Insert sample books
INSERT IGNORE INTO books_book (id, title, author_id, category_id, price, stock, description) VALUES
(1, 'Cho tôi xin một vé đi tuổi thơ', 1, 1, 85000, 50, 'Tác phẩm nổi tiếng của Nguyễn Nhật Ánh về ký niệm tuổi thơ'),
(2, 'Mắt biếc', 1, 1, 79000, 45, 'Truyện tình yêu lãng mạn của Nguyễn Nhật Ánh'),
(3, 'Tôi thấy hoa vàng trên cỏ xanh', 1, 1, 89000, 55, 'Câu chuyện tuổi thơ đầy cảm động'),
(4, 'Đắc nhân tâm', 2, 2, 120000, 100, 'Nghệ thuật đối nhân xử thế, kỹ năng giao tiếp'),
(5, 'Ngừng lo lắng và bắt đầu sống', 2, 4, 95000, 80, 'Cách sống tích cực và hạnh phúc'),
(6, 'Clean Code', 3, 3, 350000, 30, 'A Handbook of Agile Software Craftsmanship'),
(7, 'Clean Architecture', 3, 3, 380000, 25, 'A Craftsmans Guide to Software Structure'),
(8, 'Nhà giả kim', 4, 1, 89000, 60, 'Truyện về hành trình tìm kiếm kho báu'),
(9, 'Rừng Na-uy', 5, 1, 125000, 40, 'Tiểu thuyết nổi tiếng của Murakami'),
(10, 'Kafka bên bờ biển', 5, 1, 135000, 35, 'Tiểu thuyết kỳ ảo của Murakami');

-- =====================================================
-- CUSTOMER DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS customer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE customer_db;

CREATE TABLE IF NOT EXISTS customers_customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers_address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT NOT NULL,
    city VARCHAR(50),
    district VARCHAR(50),
    ward VARCHAR(50),
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customers_customer(id) ON DELETE CASCADE
);

-- Insert test customer (password: test123)
INSERT IGNORE INTO customers_customer (id, name, email, phone, password)
VALUES (1, 'Nguyễn Văn Test', 'test@example.com', '0901234567',
        'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae');

INSERT IGNORE INTO customers_address (customer_id, name, phone, address, city, district, is_default)
VALUES (1, 'Nguyễn Văn Test', '0901234567', '123 Nguyễn Văn Linh', 'TP.HCM', 'Quận 7', TRUE);

-- =====================================================
-- CART DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS cart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cart_db;

CREATE TABLE IF NOT EXISTS carts_cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS carts_cartitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(12, 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts_cart(id) ON DELETE CASCADE
);

-- Create cart for test customer
INSERT IGNORE INTO carts_cart (id, customer_id) VALUES (1, 1);

-- =====================================================
-- ORDER DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS order_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE order_db;

CREATE TABLE IF NOT EXISTS orders_order (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    shipping_address TEXT,
    shipping_method_id INT,
    payment_method_id INT,
    subtotal DECIMAL(12, 0) DEFAULT 0,
    shipping_fee DECIMAL(12, 0) DEFAULT 0,
    discount DECIMAL(12, 0) DEFAULT 0,
    total DECIMAL(12, 0) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders_orderitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    book_title VARCHAR(255),
    quantity INT DEFAULT 1,
    price DECIMAL(12, 0),
    FOREIGN KEY (order_id) REFERENCES orders_order(id) ON DELETE CASCADE
);

-- =====================================================
-- SHIPPING DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS ship_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ship_db;

CREATE TABLE IF NOT EXISTS shipping_shippingmethod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    fee DECIMAL(12, 0) DEFAULT 0,
    description TEXT,
    estimated_days VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS shipping_shipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    tracking_number VARCHAR(50),
    carrier VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert shipping methods
INSERT IGNORE INTO shipping_shippingmethod (id, name, fee, description, estimated_days) VALUES
(1, 'Giao hàng tiêu chuẩn', 25000, 'Giao hàng trong 3-5 ngày làm việc', '3-5 ngày'),
(2, 'Giao hàng nhanh', 45000, 'Giao hàng trong 1-2 ngày làm việc', '1-2 ngày'),
(3, 'Giao hàng hỏa tốc', 70000, 'Giao hàng trong ngày', 'Trong ngày');

-- =====================================================
-- PAYMENT DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS pay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pay_db;

CREATE TABLE IF NOT EXISTS payments_paymentmethod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS payments_payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method_id INT,
    amount DECIMAL(12, 0),
    status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert payment methods
INSERT IGNORE INTO payments_paymentmethod (id, name, code, description) VALUES
(1, 'Thanh toán khi nhận hàng (COD)', 'cod', 'Trả tiền mặt khi nhận hàng'),
(2, 'Chuyển khoản ngân hàng', 'bank', 'Chuyển khoản qua tài khoản ngân hàng'),
(3, 'Ví MoMo', 'momo', 'Thanh toán qua ví điện tử MoMo'),
(4, 'VNPay', 'vnpay', 'Thanh toán qua cổng VNPay');

-- =====================================================
-- COMMENT/RATING DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS comment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE comment_db;

CREATE TABLE IF NOT EXISTS reviews_review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    content TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- RECOMMENDER DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS recommender_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE recommender_db;

CREATE TABLE IF NOT EXISTS recommendations_recommendation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    book_id INT NOT NULL,
    score DECIMAL(5, 4),
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MANAGER DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS manager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'Databases created:' AS message;
SHOW DATABASES LIKE '%_db';

SELECT 'Setup complete! Sample data inserted.' AS status;
