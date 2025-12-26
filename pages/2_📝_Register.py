"""
Register Page
Trang đăng ký tài khoản mới
"""

import streamlit as st
import sys
import os
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.auth_manager import AuthManager

# Page config
st.set_page_config(
    page_title="Register - AI LeafGuard",
    page_icon="📝",
    layout="centered"
)

# Initialize auth manager
auth_manager = AuthManager()
auth_manager.init_session_state()

# Nếu đã login, redirect về home
if auth_manager.is_logged_in():
    st.success(f"✅ Bạn đã có tài khoản rồi, {st.session_state.user['display_name']}!")
    st.info("👈 Quay về trang chính để sử dụng AI diagnosis")
    
    if st.button("🏠 Về trang chính", use_container_width=True):
        st.switch_page("app.py")
    
    st.stop()

# =====================
# HELPER FUNCTIONS
# =====================

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Check password strength
    
    Returns:
        (is_valid: bool, message: str)
    """
    if len(password) < 6:
        return False, "❌ Password phải có ít nhất 6 ký tự"
    if len(password) < 8:
        return True, "⚠️ Password hơi yếu (khuyến nghị ≥8 ký tự)"
    if not any(c.isdigit() for c in password):
        return True, "⚠️ Nên thêm số để password mạnh hơn"
    if not any(c.isupper() for c in password):
        return True, "⚠️ Nên thêm chữ hoa để password mạnh hơn"
    
    return True, "✅ Password mạnh"

# =====================
# REGISTER FORM
# =====================

st.title("📝 Đăng ký tài khoản")
st.caption("Tạo tài khoản miễn phí để sử dụng AI LeafGuard")

st.divider()

with st.form("register_form"):
    display_name = st.text_input(
        "👤 Tên hiển thị",
        placeholder="Ví dụ: Nguyễn Văn A",
        help="Tên này sẽ hiển thị trong hệ thống"
    )
    
    email = st.text_input(
        "📧 Email",
        placeholder="your.email@example.com",
        help="Email sẽ được dùng để đăng nhập"
    )
    
    password = st.text_input(
        "🔑 Password",
        type="password",
        placeholder="Tối thiểu 6 ký tự",
        help="Mật khẩu nên có ít nhất 8 ký tự, bao gồm chữ hoa và số"
    )
    
    confirm_password = st.text_input(
        "🔑 Xác nhận Password",
        type="password",
        placeholder="Nhập lại mật khẩu"
    )
    
    # Password strength indicator
    if password:
        is_valid, strength_msg = check_password_strength(password)
        if "✅" in strength_msg:
            st.success(strength_msg)
        elif "⚠️" in strength_msg:
            st.warning(strength_msg)
        else:
            st.error(strength_msg)
    
    agree_terms = st.checkbox(
        "Tôi đồng ý với Điều khoản Sử dụng và Chính sách Bảo mật",
        help="Bắt buộc để đăng ký"
    )
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        submit = st.form_submit_button("🚀 Đăng ký", use_container_width=True)
    
    with col2:
        login = st.form_submit_button("🔐 Đã có tài khoản", use_container_width=True)

# Handle form submission
if submit:
    # Validation
    errors = []
    
    if not display_name:
        errors.append("❌ Vui lòng nhập tên hiển thị")
    
    if not email:
        errors.append("❌ Vui lòng nhập email")
    elif not is_valid_email(email):
        errors.append("❌ Email không hợp lệ")
    
    if not password:
        errors.append("❌ Vui lòng nhập password")
    elif len(password) < 6:
        errors.append("❌ Password phải có ít nhất 6 ký tự")
    
    if password != confirm_password:
        errors.append("❌ Password xác nhận không khớp")
    
    if not agree_terms:
        errors.append("❌ Vui lòng đồng ý với Điều khoản Sử dụng")
    
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
                st.balloons()
                st.success(message)
                st.info("🎉 Bạn có thể đăng nhập ngay bây giờ!")
                
                # Auto-login
                if auth_manager.login(email, password):
                    st.success("✅ Đang tự động đăng nhập...")
                    st.rerun()
            else:
                st.error(message)

if login:
    st.switch_page("pages/1_🔐_Login.py")

st.divider()

# Additional info
st.markdown("""
### ℹ️ Tại sao cần đăng ký?
- 💾 **Lưu lịch sử**: Tất cả kết quả chẩn đoán được lưu lại
- 📊 **Thống kê**: Xem insight về các bệnh phát hiện
- 🔐 **Bảo mật**: Dữ liệu của bạn được bảo vệ an toàn
- 🆓 **Miễn phí**: Hoàn toàn miễn phí, không giới hạn

### 🔒 Bảo mật thông tin
Mật khẩu được mã hóa và lưu trữ an toàn bởi Firebase Authentication.
Chúng tôi không bao giờ chia sẻ thông tin cá nhân của bạn.
""")
