import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import json
import sys

# Import authentication modules
from src.auth_manager import AuthManager
from src.firestore_manager import FirestoreManager

# =======================
# PAGE CONFIG
# =======================
st.set_page_config(
    page_title="AI Plant Disease Detection",
    page_icon="🌿",
    layout="centered"
)

# =======================
# INITIALIZE AUTH
# =======================
auth_manager = AuthManager()
auth_manager.init_session_state()
firestore = FirestoreManager()

# =======================
# HEADER & NAVIGATION
# =======================
st.title("🌿 AI Plant Disease Detection")
st.caption("Academic demo – Plant disease recognition using Deep Learning")

# User info in sidebar
with st.sidebar:
    st.markdown("### 🔐 Tài khoản")
    
    if auth_manager.is_logged_in():
        user = auth_manager.get_current_user()
        st.success(f"Xin chào, **{user['display_name']}**!")
        
        # Statistics
        stats = firestore.get_user_statistics(auth_manager.get_current_user_id())
        st.metric("Tổng chẩn đoán", stats.get('total_diagnoses', 0))
        
        # Navigation
        st.markdown("---")
        if st.button("👤 Profile", use_container_width=True):
            st.switch_page("pages/3_👤_Profile.py")
        if st.button("📊 Lịch sử", use_container_width=True):
            st.switch_page("pages/4_📊_History.py")
        if st.button("🚪 Đăng xuất", use_container_width=True):
            auth_manager.logout()
            st.rerun()
    else:
        st.info("Vui lòng đăng nhập để lưu lịch sử chẩn đoán")
        if st.button("🔐 Đăng nhập", use_container_width=True):
            st.switch_page("pages/1_🔐_Login.py")
        if st.button("📝 Đăng ký", use_container_width=True):
            st.switch_page("pages/2_📝_Register.py")
    
    st.markdown("---")
    st.caption("⚠️ Academic demo only")

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
# AUTH GATE (OPTIONAL)
# =======================
# Uncomment dòng dưới nếu muốn bắt buộc login
# if not auth_manager.is_logged_in():
#     st.warning("⚠️ Vui lòng đăng nhập để sử dụng tính năng chẩn đoán")
#     st.stop()

# =======================
# UI – UPLOAD IMAGE
# =======================
st.subheader("📤 Upload a leaf image")

file = st.file_uploader(
    "Supported formats: JPG, PNG, JPEG",
    type=["jpg", "png", "jpeg"]
)

if file and model and CLASS_NAMES:
    image = Image.open(file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Diagnose"):
        with st.spinner("AI is analyzing the image..."):
            preds = predict_image(image, model)

        class_idx = np.argmax(preds)
        confidence = preds[class_idx] * 100
        label = CLASS_NAMES[class_idx]

        # Split label
        plant, disease = label.split("___")
        disease = disease.replace("_", " ")

        st.success("✅ Diagnosis Complete")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌱 Plant Type", plant)
        with col2:
            st.metric("🦠 Disease Status", disease)

        st.progress(int(confidence))
        st.caption(f"Confidence: {confidence:.2f}%")

        # Confidence warning
        if confidence < 60:
            st.warning("⚠️ Low confidence prediction. Image may be outside training distribution.")

        # Healthy / Diseased message
        if "healthy" in disease.lower():
            st.info("🎉 The plant appears to be healthy.")
        else:
            st.warning("⚠️ Disease detected. Consider appropriate treatment.")

        # =======================
        # TOP-3 PREDICTIONS
        # =======================
        st.divider()
        st.subheader("📊 Top-3 Predictions")

        top3_idx = preds.argsort()[-3:][::-1]
        top3_predictions = []
        for i in top3_idx:
            lbl = CLASS_NAMES[i].replace("___", " → ").replace("_", " ")
            conf = preds[i] * 100
            st.write(f"- **{lbl}**: {conf:.2f}%")
            
            # Prepare for Firestore
            top3_predictions.append({
                'label': lbl,
                'confidence': float(conf)
            })
        
        # =======================
        # SAVE TO FIRESTORE
        # =======================
        if auth_manager.is_logged_in():
            with st.spinner("Đang lưu kết quả vào lịch sử..."):
                diagnosis_id = firestore.save_diagnosis(
                    user_id=auth_manager.get_current_user_id(),
                    plant_type=plant,
                    disease=disease,
                    confidence=float(confidence),
                    top3_predictions=top3_predictions
                )
                
                if diagnosis_id:
                    st.success("✅ Kết quả đã được lưu vào lịch sử!")
                    st.balloons()
        else:
            st.info("💡 Đăng nhập để lưu kết quả vào lịch sử của bạn!")

else:
    st.info("⬆️ Please upload an image to start diagnosis.")

st.divider()
st.caption("⚠️ This system is for academic demonstration only.")
