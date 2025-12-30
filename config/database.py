# config/database.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy các biến môi trường (không có giá trị mặc định cho password)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD')  # Bắt buộc phải có trong .env
DB_NAME = os.getenv('DB_NAME', 'leafguard_db')

# Kiểm tra password có được cung cấp không
if not DB_PASSWORD:
    raise ValueError(
        "DB_PASSWORD không được tìm thấy trong file .env!\n"
        "Vui lòng tạo file .env với nội dung:\n"
        "DB_PASSWORD=your_actual_password"
    )

# Cấu hình database
DB_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Lỗi kết nối database: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()