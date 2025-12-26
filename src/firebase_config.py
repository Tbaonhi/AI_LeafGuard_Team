"""
Firebase Configuration Module
Khởi tạo Firebase Admin SDK và Firestore client
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class FirebaseConfig:
    """Singleton class để quản lý Firebase connection"""
    
    _instance = None
    _db = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        if not self._initialized:
            try:
                self._initialize_firebase()
                self._initialized = True
            except Exception as e:
                st.error(f"❌ Firebase initialization failed: {str(e)}")
                raise
    
    def _initialize_firebase(self):
        """Private method to initialize Firebase"""
        # Kiểm tra xem Firebase đã được khởi tạo chưa
        if not firebase_admin._apps:
            # Lấy đường dẫn credentials từ environment variable hoặc default
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
            
            # Kiểm tra file tồn tại
            if not os.path.exists(cred_path):
                raise FileNotFoundError(
                    f"Firebase credentials file not found at: {cred_path}\n"
                    "Please download the service account key from Firebase Console."
                )
            
            # Khởi tạo Firebase Admin SDK
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            print("✅ Firebase initialized successfully")
        
        # Khởi tạo Firestore client
        if self._db is None:
            self._db = firestore.client()
    
    def get_db(self):
        """Get Firestore database client"""
        return self._db
    
    def get_auth(self):
        """Get Firebase Auth client"""
        return auth


# Global instance
def get_firebase_db():
    """Helper function to get Firestore database"""
    config = FirebaseConfig()
    return config.get_db()


def get_firebase_auth():
    """Helper function to get Firebase Auth"""
    config = FirebaseConfig()
    return config.get_auth()
