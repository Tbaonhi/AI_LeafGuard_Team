import streamlit as st
from firebase_admin import auth
from firebase_admin.auth import UserNotFoundError
from typing import Optional, Dict
from config.firebase_config import get_firebase_auth
from database.firestore_manager import FirestoreManager




class AuthManager:
    #Quản lý authentication operations
   
    def __init__(self):
        self.auth = get_firebase_auth()
        self.firestore = FirestoreManager()
   


   
    def init_session_state(self):
        #Initialize session state cho authentication
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'user_email' not in st.session_state:
            st.session_state.user_email = None
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
   
    def is_logged_in(self) -> bool:
        #Check if user is logged in
        return st.session_state.get('logged_in', False)
   
    def get_current_user(self) -> Optional[Dict]:
        #Get current logged in user data
        if self.is_logged_in():
            return st.session_state.get('user')
        return None
   
    def get_current_user_id(self) -> Optional[str]:
        #Get current user ID
        return st.session_state.get('user_id')
   
    def create_user(self, email: str, password: str, display_name: str = None) -> tuple[bool, Optional[str]]:
        #Tạo user mới với Firebase Auth
        try:
            # Validate inputs
            if not email or not password:
                return False, "Email và password không được để trống"
           
            if len(password) < 6:
                return False, "Password phải có ít nhất 6 ký tự"
           
            # Tạo user trong Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
           
            # Tạo user profile trong Firestore
            success = self.firestore.create_user_profile(
                user_id=user.uid,
                email=email,
                display_name=display_name
            )
           
            if success:
                return True, f"Tạo tài khoản thành công! Welcome {display_name or email}"
            else:
                return False, "Lỗi khi tạo user profile"
           
        except auth.EmailAlreadyExistsError:
            return False, "Email này đã được đăng ký"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
   
    def verify_user(self, email: str, password: str) -> tuple[bool, Optional[str], Optional[str]]:
        #Verify user credentials (simplified for demo)
        try:
            # Get user by email
            user = auth.get_user_by_email(email)
           
            # Note: Admin SDK không thể verify password trực tiếp
            # Trong thực tế, nên dùng Firebase Client SDK để sign in
            # Hoặc implement custom token authentication
           
            # Workaround: Assume password is correct nếu user exists
            # (Chỉ dùng cho demo, không dùng trong production!)
           
            # WARNING: Đây chỉ là demo. Trong production phải dùng proper auth flow.
           
            return True, user.uid, "Đăng nhập thành công!"
           
        except UserNotFoundError:
            return False, None, "Email không tồn tại"
        except Exception as e:
            return False, None, f"Lỗi: {str(e)}"
   
    def login(self, email: str, password: str) -> bool:
        #Login user và set session state
        success, user_id, message = self.verify_user(email, password)
       
        if success and user_id:
            # Get user profile từ Firestore
            user_profile = self.firestore.get_user_profile(user_id)
           
            if user_profile:
                # Set session state
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.user_email = email
                st.session_state.user = user_profile
               
                # Update last login
                self.firestore.update_last_login(user_id)
               
                st.success(message)
                return True
       
        st.error(message)
        return False
   
    def logout(self):
        #Logout user
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.success("Đã đăng xuất thành công")
   
    def reset_password(self, email: str) -> tuple[bool, str]:
        #Send password reset email
        try:
            # Kiểm tra user tồn tại
            user = auth.get_user_by_email(email)
           
            # Generate password reset link (Admin SDK)
            link = auth.generate_password_reset_link(email)
           
            # In production, send email với link này
            # Ở đây chỉ return message
            return True, f"Link reset password đã được tạo. (Production: send email)"
           
        except UserNotFoundError:
            return False, "Email không tồn tại"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
   
    def change_password(self, user_id: str, new_password: str) -> tuple[bool, str]:
        #Change user password
        try:
            if len(new_password) < 6:
                return False, "Password phải có ít nhất 6 ký tự"
           
            auth.update_user(
                user_id,
                password=new_password
            )
           
            return True, "Đổi password thành công"
           
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
   
    def update_display_name(self, user_id: str, display_name: str) -> tuple[bool, str]:
        #Update user display name
        try:
            # Update in Firebase Auth
            auth.update_user(user_id, display_name=display_name)
           
            # Update in Firestore
            self.firestore.update_user_profile(user_id, {'display_name': display_name})
           
            # Update session state
            if st.session_state.get('user_id') == user_id:
                st.session_state.user['display_name'] = display_name
           
            return True, "Cập nhật tên thành công"
           
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
   
    def delete_user(self, user_id: str) -> tuple[bool, str]:
        #Delete user account
        try:
            # Delete from Firebase Auth
            auth.delete_user(user_id)
           
            # Note: Nên xóa user data trong Firestore bằng Cloud Functions
            # hoặc manual cleanup
           
            return True, "Xóa tài khoản thành công"
           
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

