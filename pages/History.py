import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.auth_manager import AuthManager
from database.firestore_manager import FirestoreManager
from database.db_operations import get_user_diagnoses as get_user_diagnoses_mysql, delete_diagnosis as delete_diagnosis_mysql
from PIL import Image

# Page config
st.set_page_config(
    page_title="Lịch sử chẩn đoán - AI LeafGuard",
    page_icon="🌿",
    layout="wide"
)

# Initialize managers
auth_manager = AuthManager()
auth_manager.init_session_state()
firestore = FirestoreManager()

# Check authentication
if not auth_manager.is_logged_in():
    st.warning("Vui lòng đăng nhập để xem lịch sử")
    if st.button("Đăng nhập", use_container_width=True):
        st.switch_page("pages/Login.py")
    st.stop()

# Get current user
user_id = auth_manager.get_current_user_id()

st.title("Lịch sử Chẩn đoán")
st.caption("Xem lại tất cả kết quả chẩn đoán trước đây")

st.divider()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    limit = st.selectbox(
        "Số lượng hiển thị",
        options=[10, 25, 50, 100],
        index=1,
        help="Số lượng kết quả hiển thị"
    )

with col2:
    sort_by = st.selectbox(
        "Sắp xếp theo",
        options=["Mới nhất", "Cũ nhất", "Độ tin cậy cao", "Độ tin cậy thấp"],
        help="Thứ tự sắp xếp"
    )

with col3:
    if st.button("Làm mới", use_container_width=True):
        st.rerun()

st.divider()
with st.spinner("Đang tải lịch sử..."):
    diagnoses_mysql = get_user_diagnoses_mysql(firebase_user_id=user_id, limit=limit)
    diagnoses = []
    for d in diagnoses_mysql:
        diagnoses.append({
            'id': d.get('id'),
            'plant_type': d.get('plant_type', ''),
            'disease': d.get('disease_status', ''),
            'confidence': float(d.get('confidence', 0)) * 100,
            'timestamp': d.get('created_at'),
            'image_path': d.get('image_path'),
            'top3_predictions': []
        })

if not diagnoses:
    st.info("""
    Bạn chưa có lịch sử chẩn đoán nào.
    
    Hãy về trang chính và thử chẩn đoán bệnh cây để bắt đầu!
    """)
    
    if st.button("Về trang chính", use_container_width=True):
        st.switch_page("app.py")
    
    st.stop()

st.subheader(f"Tổng quan ({len(diagnoses)} kết quả)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    healthy_count = sum(1 for d in diagnoses if 'healthy' in d['disease'].lower())
    st.metric("Khỏe mạnh", healthy_count)

with col2:
    diseased_count = len(diagnoses) - healthy_count
    st.metric("Có bệnh", diseased_count)

with col3:
    avg_confidence = sum(d['confidence'] for d in diagnoses) / len(diagnoses)
    st.metric("Độ tin cậy TB", f"{avg_confidence:.1f}%")

with col4:
    unique_plants = len(set(d['plant_type'] for d in diagnoses))
    st.metric("Loại cây", unique_plants)

st.divider()

st.subheader("Chi tiết lịch sử")

tab1, tab2 = st.tabs(["Danh sách", "Bảng dữ liệu"])

with tab1:
    # List view
    for idx, diagnosis in enumerate(diagnoses, 1):
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            
            with col1:
                # Status indicator
                if 'healthy' in diagnosis['disease'].lower():
                    st.markdown("### ✓")
                else:
                    st.markdown("### ✗")
            
            with col2:
                st.markdown(f"**{diagnosis['plant_type']}**")
                st.caption(f"Bệnh: {diagnosis['disease']}")
                
                # Hiển thị ảnh nếu có
                image_path = diagnosis.get('image_path')
                if image_path and os.path.exists(image_path):
                    try:
                        img = Image.open(image_path)
                        st.image(img, caption="Ảnh đã chẩn đoán", use_container_width=True, width=200)
                    except Exception as e:
                        st.caption(f"⚠️ Không thể tải ảnh: {str(e)}")
                elif image_path:
                    st.caption(f"⚠️ Ảnh không tìm thấy: {image_path}")
            
            with col3:
                # Timestamp
                timestamp = diagnosis.get('timestamp')
                if timestamp:
                    if hasattr(timestamp, 'strftime'):
                        time_str = timestamp.strftime('%d/%m/%Y %H:%M')
                    else:
                        time_str = str(timestamp)
                    st.caption(f"{time_str}")
                
                # Confidence
                confidence = diagnosis['confidence']
                st.progress(int(confidence))
                st.caption(f"Độ tin cậy: {confidence:.1f}%")
            
            with col4:
                # Actions
                with st.expander("Chi tiết"):
                    st.markdown("**Top 3 Predictions:**")
                    for pred in diagnosis.get('top3_predictions', []):
                        st.write(f"- {pred['label']}: {pred['confidence']:.2f}%")
                    
                    # Delete button
                    if st.button(f"Xóa", key=f"delete_{diagnosis['id']}"):
                        if delete_diagnosis_mysql(diagnosis['id'], user_id):
                            st.success("Đã xóa")
                            st.rerun()
                        else:
                            st.error("Không thể xóa chẩn đoán này")
            
            st.divider()

with tab2:
    # Table view
    df_data = []
    for d in diagnoses:
        timestamp = d.get('timestamp')
        if timestamp and hasattr(timestamp, 'strftime'):
            time_str = timestamp.strftime('%d/%m/%Y %H:%M')
        else:
            time_str = str(timestamp) if timestamp else 'N/A'
        
        df_data.append({
            'Thời gian': time_str,
            'Loại cây': d['plant_type'],
            'Bệnh': d['disease'],
            'Độ tin cậy (%)': f"{d['confidence']:.1f}",
            'ID': d['id']
        })
    
    df = pd.DataFrame(df_data)
    
    # Display dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Export button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Tải xuống CSV",
        data=csv,
        file_name=f"leafguard_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

with st.expander("Insights & Recommendations"):
    st.markdown("""
    ### Phân tích dữ liệu của bạn
    
    Dựa trên lịch sử chẩn đoán, dưới đây là một số insights:
    """)
    
    if diagnoses:
        plants = [d['plant_type'] for d in diagnoses]
        most_common = max(set(plants), key=plants.count)
        
        st.info(f"""
        - Bạn chẩn đoán **{most_common}** nhiều nhất ({plants.count(most_common)} lần)
        - Tỷ lệ cây khỏe mạnh: **{(healthy_count/len(diagnoses)*100):.1f}%**
        - Độ tin cậy trung bình: **{avg_confidence:.1f}%**
        """)
        
        if avg_confidence < 70:
            st.warning("Một số kết quả có độ tin cậy thấp. Hãy chụp ảnh rõ nét hơn để có kết quả chính xác!")
