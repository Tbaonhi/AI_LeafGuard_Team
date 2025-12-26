"""
Firestore Manager Module
Quản lý operations với Firestore Database
"""

from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
from .firebase_config import get_firebase_db


class FirestoreManager:
    """Quản lý Firestore database operations"""
    
    def __init__(self):
        self.db = get_firebase_db()
        self.users_collection = self.db.collection('users')
        self.diagnoses_collection = self.db.collection('diagnoses')
    
    # =====================
    # USER OPERATIONS
    # =====================
    
    def create_user_profile(self, user_id: str, email: str, display_name: str = None) -> bool:
        """
        Tạo user profile trong Firestore
        
        Args:
            user_id: Firebase Auth UID
            email: User email
            display_name: Display name (optional)
        
        Returns:
            True nếu thành công
        """
        try:
            user_data = {
                'email': email,
                'display_name': display_name or email.split('@')[0],
                'created_at': datetime.now(),
                'total_diagnoses': 0,
                'last_login': datetime.now()
            }
            
            self.users_collection.document(user_id).set(user_data)
            return True
        except Exception as e:
            st.error(f"Error creating user profile: {str(e)}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Lấy user profile từ Firestore
        
        Args:
            user_id: Firebase Auth UID
        
        Returns:
            User data dictionary hoặc None
        """
        try:
            doc = self.users_collection.document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            st.error(f"Error getting user profile: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, data: Dict) -> bool:
        """
        Update user profile
        
        Args:
            user_id: Firebase Auth UID
            data: Dictionary với fields cần update
        
        Returns:
            True nếu thành công
        """
        try:
            self.users_collection.document(user_id).update(data)
            return True
        except Exception as e:
            st.error(f"Error updating user profile: {str(e)}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """Update last login timestamp"""
        return self.update_user_profile(user_id, {'last_login': datetime.now()})
    
    # =====================
    # DIAGNOSIS OPERATIONS
    # =====================
    
    def save_diagnosis(
        self,
        user_id: str,
        plant_type: str,
        disease: str,
        confidence: float,
        top3_predictions: List[Dict],
        image_url: str = None
    ) -> Optional[str]:
        """
        Lưu kết quả chẩn đoán vào Firestore
        
        Args:
            user_id: Firebase Auth UID
            plant_type: Loại cây
            disease: Tên bệnh
            confidence: Độ tin cậy (%)
            top3_predictions: List của top 3 predictions
            image_url: URL của ảnh (optional)
        
        Returns:
            Diagnosis ID nếu thành công, None nếu thất bại
        """
        try:
            diagnosis_data = {
                'user_id': user_id,
                'plant_type': plant_type,
                'disease': disease,
                'confidence': confidence,
                'top3_predictions': top3_predictions,
                'image_url': image_url,
                'timestamp': datetime.now()
            }
            
            # Thêm vào collection
            doc_ref = self.diagnoses_collection.add(diagnosis_data)
            diagnosis_id = doc_ref[1].id
            
            # Tăng counter trong user profile
            self.users_collection.document(user_id).update({
                'total_diagnoses': firestore.Increment(1)
            })
            
            return diagnosis_id
        except Exception as e:
            st.error(f"Error saving diagnosis: {str(e)}")
            return None
    
    def get_user_diagnoses(
        self,
        user_id: str,
        limit: int = 50,
        order_by: str = 'timestamp'
    ) -> List[Dict]:
        """
        Lấy lịch sử chẩn đoán của user
        
        Args:
            user_id: Firebase Auth UID
            limit: Số lượng kết quả tối đa
            order_by: Field để sắp xếp
        
        Returns:
            List của diagnoses
        """
        try:
            query = (
                self.diagnoses_collection
                .where('user_id', '==', user_id)
                .order_by(order_by, direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
            
            docs = query.stream()
            diagnoses = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                diagnoses.append(data)
            
            return diagnoses
        except Exception as e:
            st.error(f"Error getting diagnoses: {str(e)}")
            return []
    
    def get_diagnosis_by_id(self, diagnosis_id: str) -> Optional[Dict]:
        """Lấy diagnosis theo ID"""
        try:
            doc = self.diagnoses_collection.document(diagnosis_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            st.error(f"Error getting diagnosis: {str(e)}")
            return None
    
    def delete_diagnosis(self, diagnosis_id: str, user_id: str) -> bool:
        """
        Xóa diagnosis
        
        Args:
            diagnosis_id: ID của diagnosis cần xóa
            user_id: User ID để verify ownership
        
        Returns:
            True nếu thành công
        """
        try:
            # Verify ownership
            diagnosis = self.get_diagnosis_by_id(diagnosis_id)
            if not diagnosis or diagnosis['user_id'] != user_id:
                st.error("Unauthorized or diagnosis not found")
                return False
            
            # Delete
            self.diagnoses_collection.document(diagnosis_id).delete()
            
            # Giảm counter
            self.users_collection.document(user_id).update({
                'total_diagnoses': firestore.Increment(-1)
            })
            
            return True
        except Exception as e:
            st.error(f"Error deleting diagnosis: {str(e)}")
            return False
    
    # =====================
    # ANALYTICS
    # =====================
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """
        Lấy thống kê cho user
        
        Returns:
            Dictionary với các thống kê
        """
        try:
            # Lấy all diagnoses
            diagnoses = self.get_user_diagnoses(user_id, limit=1000)
            
            if not diagnoses:
                return {
                    'total_diagnoses': 0,
                    'most_common_plant': None,
                    'most_common_disease': None,
                    'avg_confidence': 0
                }
            
            # Calculate statistics
            plants = [d['plant_type'] for d in diagnoses]
            diseases = [d['disease'] for d in diagnoses]
            confidences = [d['confidence'] for d in diagnoses]
            
            # Most common
            most_common_plant = max(set(plants), key=plants.count) if plants else None
            most_common_disease = max(set(diseases), key=diseases.count) if diseases else None
            
            return {
                'total_diagnoses': len(diagnoses),
                'most_common_plant': most_common_plant,
                'most_common_disease': most_common_disease,
                'avg_confidence': sum(confidences) / len(confidences) if confidences else 0
            }
        except Exception as e:
            st.error(f"Error getting statistics: {str(e)}")
            return {}


# Import fix
from firebase_admin import firestore
