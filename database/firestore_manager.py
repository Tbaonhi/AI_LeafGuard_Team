"""
Firestore Manager Module
Quản lý operations với Firestore Database
"""


from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
from firebase_admin import firestore
from config.firebase_config import get_firebase_db




class FirestoreManager:
    """Quản lý Firestore database operations"""
   
    def __init__(self):
        self.db = get_firebase_db()
        self.users_collection = self.db.collection('users')
        self.diagnoses_collection = self.db.collection('diagnoses')


    def create_user_profile(self, user_id: str, email: str, display_name: str = None) -> bool:
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
        try:
            doc = self.users_collection.document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            st.error(f"Error getting user profile: {str(e)}")
            return None
   
    def update_user_profile(self, user_id: str, data: Dict) -> bool:
        try:
            self.users_collection.document(user_id).update(data)
            return True
        except Exception as e:
            st.error(f"Error updating user profile: {str(e)}")
            return False
   
    def update_last_login(self, user_id: str) -> bool:
        return self.update_user_profile(user_id, {'last_login': datetime.now()})
   
    def save_diagnosis(
        self,
        user_id: str,
        plant_type: str,
        disease: str,
        confidence: float,
        top3_predictions: List[Dict],
        image_url: str = None
    ) -> Optional[str]:
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
        #Lấy diagnosis theo ID
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
        #Xóa diagnosis
        try:
            # Kiểm tra ownership
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


    def get_user_statistics(self, user_id: str) -> Dict:
        #Lấy thống kê cho user
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