import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import json
from src.camera_input import get_image_input


from src.auth_manager import AuthManager
from database.firestore_manager import FirestoreManager
from src.ui_components import (
    render_sidebar,
    render_diagnosis_result,
    render_top3_predictions,
    inject_theme_css,
    inject_falling_leaves,
    render_hero_header
)
from src.diagnosis_handler import handle_diagnosis
from src.utils import get_plant_type_from_label
from src.camera_input import get_image_input


st.set_page_config(
    page_title="AI Chẩn Đoán Bệnh Cây Trồng",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


inject_theme_css()
inject_falling_leaves()


auth_manager = AuthManager()
auth_manager.init_session_state()
firestore = FirestoreManager()


render_hero_header()


render_sidebar(auth_manager, firestore)


@st.cache_resource
def load_model():
    model_path = "models/MobileNetV2_best.h5"
    if not os.path.exists(model_path):
        st.error("Không tìm thấy file model!")
        return None
    return tf.keras.models.load_model(model_path)


model = load_model()


@st.cache_data
def load_class_names():
    class_path = "models/class_indices.json"
    if not os.path.exists(class_path):
        st.error("Không tìm thấy file class_indices.json!")
        return None
    with open(class_path) as f:
        class_indices = json.load(f)
    return list(class_indices.keys())


CLASS_NAMES = load_class_names()


def predict_image(image, model):
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img = np.asarray(image)
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    img = img[np.newaxis, ...]
    preds = model.predict(img, verbose=0)
    return preds[0]


col1, col2 = st.columns([1, 1.4], gap="large")


with col1:
    st.markdown('<h3 style="color: #39FF14;">🧬 GIAO DIỆN QUÉT</h3>', unsafe_allow_html=True)
   
    # Get image input (upload or camera)
    image, file = get_image_input()
   
    if image:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(image, caption="Ảnh đã tải lên", use_container_width=True)
       
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CHẨN ĐOÁN", type="primary", use_container_width=True):
            with st.spinner("AI đang phân tích ảnh..."):
                preds = predict_image(image, model)
           
            # Create a file-like object for handle_diagnosis if from camera
            if file is None or not hasattr(file, 'name'):
                import io
                from datetime import datetime
               
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG')
                img_bytes.seek(0)
               
                class MockFile:
                    def __init__(self, bytes_io, filename):
                        self.bytes_io = bytes_io
                        self.name = filename
                        self.read = bytes_io.read
                        self.seek = bytes_io.seek
                       
                file = MockFile(img_bytes, f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
           
            # Process diagnosis using handler (silent mode to avoid duplicate display)
            result = handle_diagnosis(
                image=image,
                file=file,
                preds=preds,
                class_names=CLASS_NAMES,
                auth_manager=auth_manager,
                firestore=firestore,
                silent=True  # Don't display messages here, will display in col2
            )
           
            # Store result in session state for display in col2
            if result:
                st.session_state.diagnosis_result = result
                st.session_state.diagnosis_preds = preds
                st.session_state.diagnosis_raw_label = CLASS_NAMES[np.argmax(preds)]
            else:
                # Confidence too low
                st.session_state.diagnosis_result = None
                st.session_state.low_confidence = True
                st.session_state.low_confidence_value = float(preds[np.argmax(preds)] * 100)
            st.rerun()
   
    elif not image:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.5);">
            <p>Vui lòng tải ảnh hoặc chụp ảnh từ camera để bắt đầu chẩn đoán.</p>
        </div>
        """, unsafe_allow_html=True)
   
    st.markdown('</div>', unsafe_allow_html=True)


with col2:
    if 'diagnosis_result' in st.session_state and st.session_state.diagnosis_result:
        plant_name, disease_name, confidence, is_healthy = st.session_state.diagnosis_result
        preds = st.session_state.diagnosis_preds
        raw_label = st.session_state.diagnosis_raw_label
       
        # Render diagnosis result with solution
        render_diagnosis_result(plant_name, disease_name, confidence, is_healthy, raw_label=raw_label)
       
        # Get plant type for filtering top 3 predictions
        top_plant_type = get_plant_type_from_label(raw_label)
        accent_color = "#39FF14" if is_healthy else ("#FF0055" if confidence < 60 else "#FFD700")
       
        # Display top 3 predictions
        render_top3_predictions(preds, CLASS_NAMES, top_plant_type=top_plant_type, accent_color=accent_color)
    elif 'low_confidence' in st.session_state and st.session_state.low_confidence:
        # Low confidence case
        confidence = st.session_state.low_confidence_value
        st.markdown("""
        <div class="glass-card" style="border-top: 4px solid #FF0055;">
            <h2 style="color: #FF0055; margin-bottom: 20px;">⚠️ ĐỘ TIN CẬY QUÁ THẤP</h2>
            <div class="info-box" style="border-left-color: #FF0055;">
                AI chỉ tự tin <strong>{:.1f}%</strong>. Đây có thể không phải ảnh lá cây hoặc ảnh quá mờ.<br><br>
                <strong>Gợi ý:</strong> Vui lòng chụp ảnh rõ hơn hoặc đến gần lá cây hơn.
            </div>
        </div>
        """.format(confidence), unsafe_allow_html=True)
    else:
        # Placeholder
        st.markdown("""
        <div class="glass-card" style="height: 450px; display: flex; align-items: center; justify-content: center; text-align: center; border: 1px dashed rgba(57, 255, 20, 0.2);">
            <div>
                <div style="font-size: 80px; opacity: 0.2; margin-bottom: 20px;">🌿</div>
                <h3 style="color: rgba(57, 255, 20, 0.5);">ĐANG CHỜ MẪU</h3>
                <p style="color: rgba(255,255,255,0.3);">Tải ảnh để kích hoạt hệ thống chẩn đoán</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; opacity: 0.4; font-size: 0.7rem; color: #fff;">
    LEAFGUARD AI • HỆ THỐNG CHẨN ĐOÁN BỆNH CÂY TRỒNG BẰNG AI
</div>
""", unsafe_allow_html=True)

