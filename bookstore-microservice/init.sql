-- Create all databases for bookstore microservices
-- This file runs automatically when MySQL container starts

CREATE DATABASE IF NOT EXISTS staff_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS manager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS customer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS catalog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS book_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS cart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS order_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ship_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS pay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS comment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS recommender_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant all privileges to root from any host
GRANT ALL PRIVILEGES ON staff_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON manager_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON customer_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON catalog_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON book_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON cart_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON order_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ship_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON pay_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON comment_db.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON recommender_db.* TO 'root'@'%';

FLUSH PRIVILEGES;
