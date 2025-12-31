-- database/schema.sql
-- Tạo database
CREATE DATABASE IF NOT EXISTS leafguard_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE leafguard_db;

-- Liên kết với Firebase User ID (có thể NULL nếu chưa có Firebase)
CREATE TABLE IF NOT EXISTS diagnoses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firebase_user_id VARCHAR(128) DEFAULT NULL,
    image_path VARCHAR(500),
    plant_type VARCHAR(100) NOT NULL,
    disease_status VARCHAR(200) NOT NULL,
    confidence FLOAT NOT NULL,
    prediction_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_firebase_user_id (firebase_user_id),
    INDEX idx_plant_type (plant_type),
    INDEX idx_disease_status (disease_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng thống kê
CREATE TABLE IF NOT EXISTS statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    total_diagnoses INT DEFAULT 0,
    healthy_count INT DEFAULT 0,
    diseased_count INT DEFAULT 0,
    UNIQUE KEY unique_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;