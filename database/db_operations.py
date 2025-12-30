from config.database import get_connection, close_connection
from mysql.connector import Error
import json
from datetime import datetime
import numpy as np

def save_diagnosis(plant_type, disease_status, confidence, predictions, firebase_user_id=None, image_path=None):
    #Lưu kết quả chẩn đoán vào database
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Chuyển predictions thành JSON
        predictions_json = json.dumps(predictions, ensure_ascii=False)
        
        # Convert numpy types to Python native types (MySQL connector không hỗ trợ numpy types)
        if isinstance(confidence, (np.floating, np.integer)):
            confidence = float(confidence)
        else:
            confidence = float(confidence) if confidence is not None else 0.0
        
        # INSERT theo đúng thứ tự trong schema: id (auto), firebase_user_id, image_path, plant_type, disease_status, confidence, prediction_json, created_at (auto), updated_at (auto)
        query = """
        INSERT INTO diagnoses 
        (firebase_user_id, image_path, plant_type, disease_status, confidence, prediction_json)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Thứ tự values phải khớp với thứ tự trong query
        values = (firebase_user_id, image_path, plant_type, disease_status, confidence, predictions_json)
        cursor.execute(query, values)
        connection.commit()
        
        diagnosis_id = cursor.lastrowid
        print(f"Đã lưu chẩn đoán ID: {diagnosis_id}")
        return diagnosis_id
        
    except Error as e:
        print(f"Lỗi lưu dữ liệu: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def get_user_diagnoses(firebase_user_id=None, limit=10):
    #Lấy lịch sử chẩn đoán của một user hoặc tất cả nếu không có user_id
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if firebase_user_id:
            query = """
            SELECT * FROM diagnoses 
            WHERE firebase_user_id = %s
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(query, (firebase_user_id, limit))
        else:
            # Lấy tất cả nếu không có user_id
            query = """
            SELECT * FROM diagnoses 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        # Parse JSON field
        for result in results:
            if result.get('prediction_json'):
                result['prediction_json'] = json.loads(result['prediction_json'])
        
        return results
        
    except Error as e:
        print(f"Lỗi lấy dữ liệu: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def get_statistics():
    #Lấy thống kê tổng quan
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
        print(f"Lỗi lấy thống kê: {e}")
        return None
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def delete_diagnosis(diagnosis_id: int, firebase_user_id: str = None) -> bool:
    #Xóa một chẩn đoán từ database
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        if firebase_user_id:
            # Xóa với điều kiện user_id
            query = """
            DELETE FROM diagnoses 
            WHERE id = %s AND firebase_user_id = %s
            """
            cursor.execute(query, (diagnosis_id, firebase_user_id))
        else:
            # Xóa không có điều kiện user_id (admin)
            query = "DELETE FROM diagnoses WHERE id = %s"
            cursor.execute(query, (diagnosis_id,))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Đã xóa chẩn đoán ID: {diagnosis_id}")
            return True
        else:
            print(f"⚠️ Không tìm thấy chẩn đoán ID: {diagnosis_id} hoặc không có quyền xóa")
            return False
        
    except Error as e:
        print(f"❌ Lỗi xóa dữ liệu: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            close_connection(connection)

def update_statistics():
    #Cập nhật bảng statistics (có thể gọi sau mỗi lần save_diagnosis)
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
        print(f"Lỗi cập nhật thống kê: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            close_connection(connection)