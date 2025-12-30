# database/db_operations.py
from config.database import get_connection, close_connection
from mysql.connector import Error
import json
from datetime import datetime

def save_diagnosis(firebase_user_id, plant_type, disease_status, confidence, predictions, image_path=None):
    """
    Lưu kết quả chẩn đoán vào database
    
    Args:
        firebase_user_id (str): User ID từ Firebase Auth (lấy từ code Firebase của team)
        plant_type (str): Loại cây (VD: "Tomato")
        disease_status (str): Tình trạng bệnh (VD: "Bacterial spot")
        confidence (float): Độ tin cậy (0-1)
        predictions (dict): Dictionary chứa tất cả predictions {class_name: probability}
        image_path (str, optional): Đường dẫn ảnh nếu lưu file
    
    Returns:
        int: ID của record vừa tạo, hoặc False nếu lỗi
    """
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Chuyển predictions thành JSON
        predictions_json = json.dumps(predictions, ensure_ascii=False)
        
        query = """
        INSERT INTO diagnoses 
        (firebase_user_id, image_path, plant_type, disease_status, confidence, prediction_json)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        values = (firebase_user_id, image_path, plant_type, disease_status, confidence, predictions_json)
        cursor.execute(query, values)
        connection.commit()
        
        diagnosis_id = cursor.lastrowid
        print(f"✅ Đã lưu chẩn đoán ID: {diagnosis_id}")
        return diagnosis_id
        
    except Error as e:
        print(f"❌ Lỗi lưu dữ liệu: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def get_user_diagnoses(firebase_user_id, limit=10):
    """
    Lấy lịch sử chẩn đoán của một user
    
    Args:
        firebase_user_id (str): User ID từ Firebase
        limit (int): Số lượng record tối đa
    
    Returns:
        list: Danh sách các chẩn đoán
    """
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT * FROM diagnoses 
        WHERE firebase_user_id = %s
        ORDER BY created_at DESC 
        LIMIT %s
        """
        
        cursor.execute(query, (firebase_user_id, limit))
        results = cursor.fetchall()
        
        # Parse JSON field
        for result in results:
            if result.get('prediction_json'):
                result['prediction_json'] = json.loads(result['prediction_json'])
        
        return results
        
    except Error as e:
        print(f"❌ Lỗi lấy dữ liệu: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def get_statistics():
    """
    Lấy thống kê tổng quan
    
    Returns:
        dict: Thống kê hoặc None nếu lỗi
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Tổng số chẩn đoán
        cursor.execute("SELECT COUNT(*) as total FROM diagnoses")
        total = cursor.fetchone()['total']
        
        # Số lượng healthy
        cursor.execute("SELECT COUNT(*) as healthy FROM diagnoses WHERE disease_status LIKE '%healthy%'")
        healthy = cursor.fetchone()['healthy']
        
        # Số lượng diseased
        cursor.execute("SELECT COUNT(*) as diseased FROM diagnoses WHERE disease_status NOT LIKE '%healthy%'")
        diseased = cursor.fetchone()['diseased']
        
        # Top diseases
        cursor.execute("""
            SELECT disease_status, COUNT(*) as count 
            FROM diagnoses 
            WHERE disease_status NOT LIKE '%healthy%'
            GROUP BY disease_status 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_diseases = cursor.fetchall()
        
        return {
            'total': total,
            'healthy': healthy,
            'diseased': diseased,
            'top_diseases': top_diseases
        }
        
    except Error as e:
        print(f"❌ Lỗi lấy thống kê: {e}")
        return None
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def update_statistics():
    """
    Cập nhật bảng statistics (có thể gọi sau mỗi lần save_diagnosis)
    """
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        today = datetime.now().date()
        
        # Đếm số chẩn đoán hôm nay
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN disease_status LIKE '%healthy%' THEN 1 ELSE 0 END) as healthy,
                SUM(CASE WHEN disease_status NOT LIKE '%healthy%' THEN 1 ELSE 0 END) as diseased
            FROM diagnoses 
            WHERE DATE(created_at) = %s
        """, (today,))
        
        result = cursor.fetchone()
        
        # Insert hoặc update
        cursor.execute("""
            INSERT INTO statistics (date, total_diagnoses, healthy_count, diseased_count)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_diagnoses = VALUES(total_diagnoses),
                healthy_count = VALUES(healthy_count),
                diseased_count = VALUES(diseased_count)
        """, (today, result[0], result[1], result[2]))
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"❌ Lỗi cập nhật thống kê: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            close_connection(connection)