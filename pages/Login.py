import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.auth_manager import AuthManager

# Page config
st.set_page_config(
    page_title="Đăng nhập - AI LeafGuard",
    page_icon="🌿",
    layout="centered"
)

# Initialize auth manager
auth_manager = AuthManager()
auth_manager.init_session_state()

# Nếu đã login, redirect về home
if auth_manager.is_logged_in():
    st.success(f"Bạn đã đăng nhập rồi, {st.session_state.user['display_name']}!")
    st.info("Quay về trang chính để sử dụng AI diagnosis")
    
    if st.button("Về trang chính", use_container_width=True):
        st.switch_page("app.py")
    
    st.stop()

st.title("Đăng nhập")
st.caption("Đăng nhập để sử dụng AI LeafGuard và lưu lịch sử chẩn đoán")

st.divider()

with st.form("login_form"):
    email = st.text_input(
        "Email",
        placeholder="your.email@example.com",
        help="Nhập email đã đăng ký"
    )
    
    password = st.text_input(
        "Mật khẩu",
        type="password",
        placeholder="Nhập mật khẩu",
        help="Mật khẩu nên có ít nhất 8 ký tự"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        submit = st.form_submit_button("Đăng nhập", use_container_width=True, type="primary")
    
    with col2:
        register = st.form_submit_button("Đăng ký", use_container_width=True)

# Handle form submission
if submit:
    if not email or not password:
        st.error("Vui lòng nhập đầy đủ email và mật khẩu")
    else:
        with st.spinner("Đang đăng nhập..."):
            success = auth_manager.login(email, password)
            
            if success:
                st.success("Đăng nhập thành công! Đang chuyển hướng...")
                st.rerun()

if register:
    st.switch_page("pages/Register.py")

st.divider()

