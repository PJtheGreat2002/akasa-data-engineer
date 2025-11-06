CREATE DATABASE IF NOT EXISTS akasa_db;
USE akasa_db;

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id VARCHAR(25) PRIMARY KEY,
    customer_name VARCHAR(25) NOT NULL,
    mobile_number VARCHAR(20) UNIQUE NOT NULL,
    region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_mobile (mobile_number),
    INDEX idx_region (region)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE orders (
    order_id VARCHAR(25) PRIMARY KEY,
    mobile_number VARCHAR(20) NOT NULL,
    order_date_time TIMESTAMP NOT NULL,
    sku_id VARCHAR(100) NOT NULL,
    sku_count INT NOT NULL CHECK (sku_count > 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_mobile (mobile_number),
    INDEX idx_order_date (order_date_time),
    INDEX idx_sku (sku_id),
    INDEX idx_composite (mobile_number, order_date_time),
    FOREIGN KEY (mobile_number) REFERENCES customers(mobile_number) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE OR REPLACE VIEW customer_order_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.mobile_number,
    c.region,
    COUNT(o.order_id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_spend,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    MAX(o.order_date_time) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.mobile_number = o.mobile_number
GROUP BY c.customer_id, c.customer_name, c.mobile_number, c.region;

GRANT ALL PRIVILEGES ON akasa_db.* TO 'akasa_user'@'%';
FLUSH PRIVILEGES;

SELECT 'Database setup completed successfully!' AS Status;