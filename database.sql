
-- Bank Management System
-- Database Setup
-- Database: bank managment

CREATE DATABASE IF NOT EXISTS `bank managment`;

USE `bank managment`;

-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT(11) NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (admin_id),
    UNIQUE KEY (username)
);

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT(11) NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    address VARCHAR(255) DEFAULT NULL,
    password VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id)
);

-- 3. Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    account_id INT(11) NOT NULL AUTO_INCREMENT,
    customer_id INT(11) NOT NULL,
    account_number VARCHAR(30) DEFAULT NULL,
    account_type VARCHAR(30) DEFAULT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Active',
    PRIMARY KEY (account_id),
    UNIQUE KEY (account_number),
    KEY (customer_id)
);

-- 4. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT(11) NOT NULL AUTO_INCREMENT,
    account_id INT(11) NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (transaction_id),
    KEY (account_id)
);

-- Default admin account
-- Add this only if the username does not already exist.
INSERT INTO admins (username, password)
SELECT 'admin', 'admin123'
WHERE NOT EXISTS (
    SELECT 1 FROM admins WHERE username = 'admin'
);
