import streamlit as st
import sys
import os
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.auth_manager import AuthManager

# Page config
st.set_page_config(
    page_title="Đăng ký tài khoản - AI LeafGuard",
    page_icon="🌿",
    layout="centered"
)

# Initialize auth manager
auth_manager = AuthManager()
auth_manager.init_session_state()

# Nếu đã login, redirect về home
if auth_manager.is_logged_in():
    st.success(f"Bạn đã có tài khoản rồi, {st.session_state.user['display_name']}!")
    st.info("Quay về trang chính để sử dụng AI diagnosis")
    
    if st.button("Về trang chính", use_container_width=True):
        st.switch_page("app.py")
    
    st.stop()

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return True, "Mật khẩu hơi yếu (khuyến nghị ≥8 ký tự)"
    if not any(c.isdigit() for c in password):
        return True, "Nên thêm số để mật khẩu mạnh hơn"
    if not any(c.isupper() for c in password):
        return True, "Nên thêm chữ hoa để mật khẩu mạnh hơn"
    
    return True, "Mật khẩu mạnh"


st.title("Đăng ký")
st.caption("Tạo tài khoản miễn phí để sử dụng AI LeafGuard")

st.divider()

with st.form("register_form"):
    display_name = st.text_input(
        "Tên người dùng",
        placeholder="",
    )
    
    email = st.text_input(
        "Email",
        placeholder="",
    )
    
    password = st.text_input(
        "Mật khẩu",
        type="password",
        placeholder="",
        help="Mật khẩu nên có ít nhất 8 ký tự, bao gồm chữ hoa và số"
    )
    
    confirm_password = st.text_input(
        "Xác nhận mật khẩu",
        type="password",
        placeholder="",
    )
    
    # Password strength indicator
    if password:
        is_valid, strength_msg = check_password_strength(password)
        # Remove emoji from message
        clean_msg = strength_msg.replace("✅", "").replace("⚠️", "").replace("❌", "").strip()
        if "Mật khẩu mạnh" in strength_msg:
            st.success(clean_msg)
        elif "Mật khẩu hơi yếu" in strength_msg or "Nên thêm" in strength_msg:
            st.warning(clean_msg)
        else:
            st.error(clean_msg)
    st.divider()
    agree_terms = st.checkbox(
        "Tôi đồng ý với Điều khoản Sử dụng và Chính sách Bảo mật",
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        submit = st.form_submit_button("Đăng ký", use_container_width=True, type="primary")
    
    with col2:
        login = st.form_submit_button("Đã có tài khoản? Đăng nhập", use_container_width=True)

# Handle form submission
if submit:
    # Validation
    errors = []
    
    if not display_name:
        errors.append("Vui lòng nhập tên hiển thị")
    
    if not email:
        errors.append("Vui lòng nhập email")
    elif not is_valid_email(email):
        errors.append("Email không hợp lệ")
    
    if not password:
        errors.append("Vui lòng nhập mật khẩu")
    elif len(password) < 8:
        errors.append("Mật khẩu nên có ít nhất 8 ký tự")
    
    if password != confirm_password:
        errors.append("Mật khẩu xác nhận không khớp")
    
    if not agree_terms:
        errors.append("Vui lòng đồng ý với Điều khoản Sử dụng")
    
    # Show errors or create account
    if errors:
        for error in errors:
            st.error(error)
    else:
        with st.spinner("Đang tạo tài khoản..."):
            success, message = auth_manager.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            if success:
                st.success(message)
                st.info("Bạn có thể đăng nhập ngay bây giờ!")
                
                # Auto-login
                if auth_manager.login(email, password):
                    st.success("Đang tự động đăng nhập...")
                    st.rerun()
            else:
                st.error(message)

if login:
    st.switch_page("pages/Login.py")

st.divider()



