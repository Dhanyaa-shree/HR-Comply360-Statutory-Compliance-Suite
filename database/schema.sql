-- Create Database
CREATE DATABASE IF NOT EXISTS hr_comply360;
USE hr_comply360;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compliance Table
CREATE TABLE IF NOT EXISTS compliance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    serial_no INT,
    authority VARCHAR(100) NOT NULL,
    compliance_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    valid_date DATE NOT NULL,
    submission_date DATE,
    process_time VARCHAR(50),
    frequency VARCHAR(50),
    reminder_days VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(20) DEFAULT 'Planned',
    remarks TEXT,
    completion_date DATE,
    updated_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_authority (authority),
    INDEX idx_status (status),
    INDEX idx_valid_date (valid_date)
);

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    compliance_id INT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compliance_id) REFERENCES compliance(id) ON DELETE CASCADE
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'Info',
    is_read BOOLEAN DEFAULT FALSE,
    compliance_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (compliance_id) REFERENCES compliance(id) ON DELETE CASCADE
);

-- Email Logs Table
CREATE TABLE IF NOT EXISTS email_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    compliance_id INT,
    recipient_email VARCHAR(100),
    subject VARCHAR(255),
    message TEXT,
    reminder_type VARCHAR(50),
    email_status VARCHAR(20) DEFAULT 'Pending',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (compliance_id) REFERENCES compliance(id) ON DELETE CASCADE
);

-- Import Logs Table
CREATE TABLE IF NOT EXISTS import_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255),
    records_count INT,
    success_count INT,
    error_count INT,
    errors JSON,
    status VARCHAR(20) DEFAULT 'Pending',
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Default HR User (password: password123)
INSERT INTO users (name, email, password_hash) 
VALUES ('HR Admin', 'hr@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYyQJvM7QkqEVM2');