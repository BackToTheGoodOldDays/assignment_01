-- =====================================================
-- SQL Script for Microservices Bookstore Databases
-- Creates separate databases for each service
-- =====================================================

-- =====================================================
-- Customer Service Database
-- =====================================================
CREATE DATABASE IF NOT EXISTS bookstore_micro_customers CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore_micro_customers;

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Book Service Database
-- =====================================================
CREATE DATABASE IF NOT EXISTS bookstore_micro_books CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore_micro_books;

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT UNSIGNED DEFAULT 0,
    description TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample Books Data
INSERT INTO books (title, author, price, stock, description) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 12.99, 50, 'A story of decadence and excess.'),
('To Kill a Mockingbird', 'Harper Lee', 14.99, 35, 'A classic of modern American literature.'),
('1984', 'George Orwell', 11.99, 40, 'A dystopian social science fiction novel.'),
('Pride and Prejudice', 'Jane Austen', 9.99, 60, 'A romantic novel of manners.'),
('The Catcher in the Rye', 'J.D. Salinger', 10.99, 25, 'A story about teenage angst and alienation.'),
('Harry Potter and the Sorcerer''s Stone', 'J.K. Rowling', 19.99, 100, 'The first book in the Harry Potter series.'),
('The Lord of the Rings', 'J.R.R. Tolkien', 24.99, 30, 'An epic high-fantasy novel.'),
('The Hobbit', 'J.R.R. Tolkien', 15.99, 45, 'A fantasy novel and prequel to The Lord of the Rings.'),
('Clean Code', 'Robert C. Martin', 34.99, 20, 'A handbook of agile software craftsmanship.'),
('Design Patterns', 'Gang of Four', 44.99, 15, 'Elements of reusable object-oriented software.');

-- =====================================================
-- Cart Service Database
-- =====================================================
CREATE DATABASE IF NOT EXISTS bookstore_micro_carts CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore_micro_carts;

-- Carts table (customer_id references customer-service)
CREATE TABLE IF NOT EXISTS carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_customer_id (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart Items table (book_id references book-service)
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    book_title VARCHAR(255) NOT NULL,
    book_author VARCHAR(255) NOT NULL,
    book_price DECIMAL(10, 2) NOT NULL,
    quantity INT UNSIGNED DEFAULT 1,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_book (cart_id, book_id),
    INDEX idx_cart_id (cart_id),
    INDEX idx_book_id (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
