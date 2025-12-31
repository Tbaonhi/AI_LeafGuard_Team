import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.auth_manager import AuthManager
from database.firestore_manager import FirestoreManager

# Page config
st.set_page_config(
    page_title="Thông tin cá nhân - AI LeafGuard",
    page_icon="🌿",
    layout="centered"
)

# Initialize managers
auth_manager = AuthManager()
auth_manager.init_session_state()
firestore = FirestoreManager()

# Check authentication
if not auth_manager.is_logged_in():
    st.warning("Vui lòng đăng nhập để xem profile")
    if st.button("Đăng nhập", use_container_width=True):
        st.switch_page("pages/Login.py")
    st.stop()

# Get current user
user = auth_manager.get_current_user()
user_id = auth_manager.get_current_user_id()

st.title("Thông tin cá nhân")
st.caption(f"Quản lý thông tin cá nhân của bạn")

st.divider()

st.subheader("Thông tin cá nhân")

col1, col2 = st.columns([1, 2])

with col1:
    # Avatar placeholder
    st.markdown(f"""
    <div style='
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        color: white;
        font-weight: bold;
    '>
        {user['display_name'][0].upper() if user.get('display_name') else '?'}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"### {user.get('display_name', 'User')}")
    st.markdown(f"Email: {user.get('email', 'N/A')}")
    
    if user.get('created_at'):
        created = user['created_at']
        if hasattr(created, 'strftime'):
            st.caption(f"Tham gia: {created.strftime('%d/%m/%Y')}")

st.divider()

st.subheader("Thống kê")

# Get statistics
stats = firestore.get_user_statistics(user_id)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tổng chẩn đoán",
        stats.get('total_diagnoses', 0),
        help="Tổng số lần bạn đã sử dụng AI diagnosis"
    )

with col2:
    most_plant = stats.get('most_common_plant', 'N/A')
    st.metric(
        "Cây phổ biến nhất",
        most_plant if most_plant else 'Chưa có dữ liệu',
        help="Loại cây bạn chẩn đoán nhiều nhất"
    )

with col3:
    avg_conf = stats.get('avg_confidence', 0)
    st.metric(
        "Độ tin cậy TB",
        f"{avg_conf:.1f}%" if avg_conf > 0 else 'N/A',
        help="Độ tin cậy trung bình của các chẩn đoán"
    )

if stats.get('most_common_disease'):
    st.info(f"Bệnh phát hiện nhiều nhất: **{stats['most_common_disease']}**")

st.divider()

st.subheader("Chỉnh sửa thông tin")

with st.form("edit_profile_form"):
    new_display_name = st.text_input(
        "Tên người dùng",
        value=user.get('display_name', ''),
    )
    
    submit_name = st.form_submit_button("Lưu thay đổi", use_container_width=True, type="primary")
    
    if submit_name:
        if new_display_name and new_display_name != user.get('display_name'):
            success, message = auth_manager.update_display_name(user_id, new_display_name)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.info("Không có thay đổi nào")

st.divider()

# =====================
# CHANGE PASSWORD
# =====================

st.subheader("Đổi mật khẩu")

with st.form("change_password_form"):
    new_password = st.text_input(
        "Mật khẩu mới",
        type="password",
        placeholder="",
    )
    
    confirm_new_password = st.text_input(
        "Xác nhận mật khẩu mới",
        type="password",
        placeholder="",
    )
    
    submit_password = st.form_submit_button("Đổi mật khẩu", use_container_width=True, type="primary")
    
    if submit_password:
        if not new_password:
            st.error("Vui lòng nhập mật khẩu mới")
        elif new_password != confirm_new_password:
            st.error("Mật khẩu xác nhận không khớp")
        else:
            success, message = auth_manager.change_password(user_id, new_password)
            if success:
                st.success(message)
            else:
                st.error(message)

st.divider()

st.subheader("Đăng xuất")

if st.button("Đăng xuất", use_container_width=True, type="primary"):
    auth_manager.logout()
    st.rerun()

with st.expander("Khu vực nguy hiểm"):
    st.warning("""
    **Cảnh báo**: Các hành động dưới đây không thể hoàn tác!
    """)
    
    if st.button("Xóa tài khoản", type="secondary"):
        st.error("Tính năng này đang được phát triển. Vui lòng liên hệ admin để xóa tài khoản.")
