# database/init_db.py
import mysql.connector
from mysql.connector import Error
import os
import sys

# Thêm parent directory vào path để import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import DB_CONFIG

def init_database():
    #Khởi tạo database và các bảng tự động
    try:
        # Kết nối không chỉ định database để tạo database mới
        config_no_db = DB_CONFIG.copy()
        db_name = config_no_db.pop('database', 'leafguard_db')
        
        print("Đang kết nối đến MySQL server...")
        connection = mysql.connector.connect(**config_no_db)
        cursor = connection.cursor()
        
        # Đọc file schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"Không tìm thấy file: {schema_path}")
            return False
        
        print(f"Đang đọc schema từ: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Thực thi từng câu lệnh SQL (tách bằng dấu ;)
        print("Đang tạo database và các bảng...")
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                print(f"  Câu lệnh {i}/{len(statements)} đã thực thi")
            except Error as e:
                # Bỏ qua lỗi nếu bảng đã tồn tại
                if "already exists" not in str(e).lower():
                    print(f"  Lỗi ở câu lệnh {i}: {e}")
        
        connection.commit()
        print("\nDatabase đã được khởi tạo thành công!")
        print(f"Database: {db_name}")
        print("Các bảng đã tạo:")
        cursor.execute(f"USE {db_name}")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        return True
        
    except Error as e:
        print(f"Lỗi khởi tạo database: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nĐã đóng kết nối.")

if __name__ == "__main__":
    # Kiểm tra file .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        print("Cảnh báo: Không tìm thấy file .env")
        print("   Đang sử dụng cấu hình mặc định từ config/database.py")
        print()
    
    success = init_database()
    sys.exit(0 if success else 1)