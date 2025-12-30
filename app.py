import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import json
from database.db_operations import save_diagnosis, get_user_diagnoses, get_statistics, update_statistics
from camera_input import get_image_input

# =======================
# PAGE CONFIG
# =======================
st.set_page_config(
    page_title="AI Plant Disease Detection",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 AI Plant Disease Detection")
st.caption("Academic demo – Plant disease recognition using Deep Learning")

# =======================
# HELPER: GET FIREBASE USER ID
# =======================
def get_firebase_user_id():
    """
    Lấy Firebase User ID từ session state hoặc Firebase Auth
    TODO: Thay thế bằng code Firebase thực tế từ team member
    """
    # Tạm thời: dùng session state hoặc giá trị demo
    if 'user_id' not in st.session_state:
        # Nếu chưa có Firebase code, dùng giá trị demo
        # Khi có Firebase code, thay bằng: return get_current_user_id() hoặc tương tự
        st.session_state['user_id'] = 'demo_user_123'  # Giá trị tạm thời
    
    return st.session_state.get('user_id', 'demo_user_123')

# =======================
# SIDEBAR: HISTORY & STATISTICS
# =======================
with st.sidebar:
    st.header("📊 Database Features")
    
    tab1, tab2 = st.tabs(["📜 History", "📈 Statistics"])
    
    with tab1:
        st.subheader("Your Diagnosis History")
        firebase_user_id = get_firebase_user_id()
        
        if st.button("🔄 Refresh History"):
            st.rerun()
        
        diagnoses = get_user_diagnoses(firebase_user_id, limit=10)
        
        if diagnoses:
            st.write(f"**Found {len(diagnoses)} recent diagnoses:**")
            for idx, diag in enumerate(diagnoses, 1):
                with st.expander(f"#{idx} - {diag['plant_type']} ({diag['created_at'].strftime('%Y-%m-%d %H:%M')})"):
                    st.write(f"**Disease:** {diag['disease_status']}")
                    st.write(f"**Confidence:** {diag['confidence']*100:.2f}%")
                    st.write(f"**Date:** {diag['created_at']}")
        else:
            st.info("No diagnosis history found.")
    
    with tab2:
        st.subheader("Overall Statistics")
        
        if st.button("🔄 Refresh Stats"):
            st.rerun()
        
        stats = get_statistics()
        
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Diagnoses", stats['total'])
            with col2:
                st.metric("Healthy", stats['healthy'])
            
            st.metric("Diseased", stats['diseased'])
            
            if stats['top_diseases']:
                st.write("**Top 5 Diseases:**")
                for disease in stats['top_diseases']:
                    st.write(f"- {disease['disease_status']}: {disease['count']} cases")
        else:
            st.info("No statistics available yet.")

st.divider()

# =======================
# LOAD MODEL (CACHE)
# =======================
@st.cache_resource
def load_model():
    model_path = "models/MobileNetV2_best.h5"
    if not os.path.exists(model_path):
        st.error("❌ Model file not found!")
        return None
    return tf.keras.models.load_model(model_path)

model = load_model()

# =======================
# LOAD CLASS NAMES (SAFE)
# =======================
@st.cache_data
def load_class_names():
    class_path = "models/class_indices.json"
    if not os.path.exists(class_path):
        st.error("❌ class_indices.json not found!")
        return None
    with open(class_path) as f:
        class_indices = json.load(f)
    return list(class_indices.keys())

CLASS_NAMES = load_class_names()

# =======================
# PREDICTION FUNCTION
# =======================
def predict_image(image, model):
    size = (224, 224)

    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img = np.asarray(image)

    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    img = img[np.newaxis, ...]

    preds = model.predict(img)
    return preds[0]

# =======================
# UI – IMAGE INPUT
# =======================
image = get_image_input()



if image is not None and model and CLASS_NAMES:
    st.image(image, caption="Input Image", use_container_width=True)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Diagnose"):
        with st.spinner("AI is analyzing the image..."):
            preds = predict_image(image, model)

        class_idx = np.argmax(preds)
        confidence = preds[class_idx] * 100
        raw_label = CLASS_NAMES[class_idx]

        # =======================
        # CONFIDENCE THRESHOLD CHECK
        # =======================
        CONFIDENCE_THRESHOLD = 60.0  # Ngưỡng an toàn là 60%

        st.divider()
        
        # Nếu độ tin cậy quá thấp -> Từ chối chẩn đoán
        if confidence < CONFIDENCE_THRESHOLD:
            st.error("⚠️ LOW CONFIDENCE / CANNOT IDENTIFY")
            st.write(f"AI is only **{confidence:.2f}%** confident. This may not be a leaf image or the image is too blurry.")
            st.info("💡 Tip: Please take a clearer photo or get closer to the leaf.")
            
            # Vẫn hiện Top 3 để tham khảo (nhưng ghi chú rõ)
            st.subheader("🔍 AI 'Suspected' Results (Reference Only):")
            
            # Không lưu vào database nếu confidence quá thấp
        else:
            # Nếu độ tin cậy cao -> Hiển thị kết quả bình thường
            
            # =======================
            # SMART LABEL PROCESSING
            # =======================
            # Thay thế 3 gạch bằng 1 gạch, rồi tách
            clean_label = raw_label.replace("___", "_")
            parts = clean_label.split("_")
            
            # Lấy phần đầu làm tên cây, phần sau làm tên bệnh
            plant_name = parts[0]
            disease_name = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"

            # Xử lý healthy đặc biệt
            if "healthy" in clean_label.lower():
                disease_name = "Healthy"
                st.balloons()  # Hiệu ứng balloons khi healthy
            
            st.success("✅ Diagnosis Complete")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🌱 Plant Type", plant_name)
            with col2:
                st.metric("🦠 Disease Status", disease_name)

            st.progress(int(confidence))
            st.caption(f"Confidence: {confidence:.2f}%")
            
            # Healthy / Diseased message
            if "healthy" in disease_name.lower():
                st.info("🎉 The plant appears to be developing well.")
            else:
                st.warning("⚠️ Disease detected. Please monitor and treat accordingly.")

            # =======================
            # SAVE TO DATABASE
            # =======================
            firebase_user_id = get_firebase_user_id()
            
            # Tạo dictionary predictions cho tất cả classes
            predictions_dict = {CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))}
            
            # Lưu vào database
            try:
                diagnosis_id = save_diagnosis(
                    firebase_user_id=firebase_user_id,
                    plant_type=plant_name,
                    disease_status=disease_name,
                    confidence=confidence / 100.0,  # Chuyển từ % sang 0-1
                    predictions=predictions_dict,
                    image_path=None  # Có thể lưu ảnh nếu cần
                )
                
                if diagnosis_id:
                    st.success(f"💾 Diagnosis saved to database (ID: {diagnosis_id})")
                    # Cập nhật thống kê
                    update_statistics()
                else:
                    st.warning("⚠️ Could not save to database. Check database connection.")
            except Exception as e:
                st.warning(f"⚠️ Database error: {str(e)}")

        # =======================
        # TOP-3 PREDICTIONS (ALWAYS SHOW)
        # =======================
        st.divider()
        with st.expander("📊 View detailed probabilities (Top 3)", expanded=False):
            top3_idx = preds.argsort()[-3:][::-1]
            for i in top3_idx:
                lbl = CLASS_NAMES[i].replace("___", " - ").replace("_", " ")
                prob = preds[i] * 100
                st.write(f"- **{lbl}**: {prob:.2f}%")

else:
    st.info("⬆️ Please upload an image to start diagnosis.")

st.divider()
st.caption("⚠️ This system is for academic demonstration only.")
