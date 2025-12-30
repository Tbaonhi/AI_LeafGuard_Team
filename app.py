import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import json
import time
import random

# =======================
# 1. SETUP PAGE
# =======================
st.set_page_config(
    page_title="LeafGuard AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =======================
# 2. BIO-DIGITAL CSS THEME
# =======================
st.markdown("""
<style>
/* IMPORT FONTS */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Outfit:wght@300;400;600&display=swap');

:root {
    --neon-green: #39FF14;     /* Màu xanh Neon lá cây rực rỡ hơn */
    --neon-accent: #00FFA3;
    --glass-bg: rgba(10, 20, 15, 0.7);
    --glass-border: rgba(57, 255, 20, 0.3);
    --text-primary: #F0FFF0;
}

* {
    font-family: 'Outfit', sans-serif;
}

h1, h2, h3, .hero-text {
    font-family: 'Rajdhani', sans-serif !important;
    text-transform: uppercase;
}

/* === 1. ANIMATED JUNGLE BACKGROUND === */
div[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 50%, #0a2e1e 0%, #000000 100%);
    background-size: 100% 100%;
    color: var(--text-primary);
}

/* === 2. FALLING LEAVES ANIMATION === */
.leaf {
    position: fixed;
    top: -10%;
    z-index: 0;
    user-select: none;
    pointer-events: none;
    animation: falling linear infinite;
    opacity: 0.3;
    font-size: 20px;
}

@keyframes falling {
    0% { transform: translateY(0) rotate(0deg); opacity: 0; }
    20% { opacity: 0.5; }
    100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
}

/* === 3. GLOWING TEXT FIX === */
.glowing-text {
    font-size: 5rem;
    font-weight: 800;
    color: #fff;
    text-shadow: 
        0 0 10px #000, 
        0 0 20px var(--neon-green), 
        0 0 40px var(--neon-green);
    animation: pulseText 3s infinite alternate;
}

@keyframes pulseText {
    from { text-shadow: 0 0 20px var(--neon-green); }
    to { text-shadow: 0 0 30px var(--neon-accent), 0 0 10px #fff; }
}

/* === 4. GLASS CARDS === */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 30px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    margin-bottom: 24px;
    position: relative;
    z-index: 1;
}

/* === 5. CIRCULAR PROGRESS (UPDATED STYLE) === */
.progress-container {
    position: relative;
    width: 150px;
    height: 150px;
    margin-left: auto; /* Align right in column */
}

.circular-chart {
    display: block;
    margin: 0 auto;
    max-width: 100%;
    max-height: 100%;
}

.circle-bg {
    fill: none;
    stroke: rgba(255, 255, 255, 0.1);
    stroke-width: 2.5; /* Thinner background ring */
}

.circle {
    fill: none;
    stroke-width: 2.5; /* Match width */
    stroke-linecap: round;
    animation: progress 1s ease-out forwards;
    transform-origin: center;
    transform: rotate(-90deg); /* Start from top */
}

.percentage-text {
    fill: #fff;
    font-family: 'Rajdhani', sans-serif;
    font-weight: bold;
    font-size: 0.5em; /* Adjusted font size */
    text-anchor: middle;
    text-shadow: 0 0 5px rgba(0,0,0,0.5);
}

.label-text {
    fill: #fff;
    font-family: 'Outfit', sans-serif;
    font-size: 0.15em;
    text-anchor: middle;
    opacity: 0.7;
}

@keyframes progress {
    0% { stroke-dasharray: 0, 100; }
}

/* Info Box */
.info-box {
    background: rgba(57, 255, 20, 0.1);
    border-left: 4px solid var(--neon-green);
    padding: 20px;
    border-radius: 0 12px 12px 0;
    color: #E0FFE0;
    font-size: 1.05rem;
    line-height: 1.6;
    margin-top: 15px;
}

/* Upload Zone */
.upload-zone {
    border: 2px dashed rgba(57, 255, 20, 0.4);
    border-radius: 20px;
    background: rgba(0, 0, 0, 0.3);
    padding: 40px;
    text-align: center;
    transition: 0.3s;
}
.upload-zone:hover {
    background: rgba(57, 255, 20, 0.1);
    border-color: var(--neon-green);
    box-shadow: 0 0 20px rgba(57, 255, 20, 0.2);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, transparent 0%, rgba(57, 255, 20, 0.1) 50%, transparent 100%);
    color: var(--neon-green);
    border: 1px solid var(--neon-green);
    border-radius: 12px;
    padding: 15px 30px;
    font-weight: 700;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 2px;
    width: 100%;
    transition: all 0.3s;
}
.stButton > button:hover {
    background: var(--neon-green);
    color: #000;
    box-shadow: 0 0 30px var(--neon-green);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 8px;
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: rgba(255,255,255,0.6);
    border: none;
    font-weight: 600;
    border-radius: 10px;
}
.stTabs [aria-selected="true"] {
    background: rgba(57, 255, 20, 0.15) !important;
    color: var(--neon-green) !important;
    border: 1px solid var(--neon-green);
}

div[data-testid="stHeader"], footer { display: none; }
.block-container { padding-top: 2rem; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)

# --- INJECT FALLING LEAVES HTML ---
leaves_html = ""
for i in range(15):
    left = random.randint(0, 100)
    delay = random.uniform(0, 10)
    duration = random.uniform(10, 20)
    icon = random.choice(["🌿", "🍃", "🍂", "☘️"])
    leaves_html += f'<div class="leaf" style="left: {left}%; animation-delay: {delay}s; animation-duration: {duration}s;">{icon}</div>'
st.markdown(leaves_html, unsafe_allow_html=True)

# =======================
# 3. BACKEND LOGIC
# =======================
@st.cache_resource
def load_ai_model():
    path = "models/MobileNetV2_best.h5" 
    if os.path.exists(path): return tf.keras.models.load_model(path)
    return None

@st.cache_data
def load_metadata():
    c_path = "models/class_indices.json"
    d_path = "data/disease_info.json"
    classes = []
    if os.path.exists(c_path):
        with open(c_path, 'r', encoding='utf-8') as f:
            classes = [k for k, v in sorted(json.load(f).items(), key=lambda x: x[1])]
    info = {}
    if os.path.exists(d_path):
        with open(d_path, 'r', encoding='utf-8') as f: info = json.load(f)
    return classes, info

model = load_ai_model()
CLASSES, INFO = load_metadata()

def get_prediction(img, model):
    if not model: return None
    img = ImageOps.fit(img, (224, 224), Image.Resampling.LANCZOS)
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(np.array(img)[np.newaxis, ...])
    preds = model.predict(arr, verbose=0)[0]
    
    top_3 = np.argsort(preds)[-3:][::-1]
    results = []
    for i in top_3:
        if i < len(CLASSES):
            label = CLASSES[i]
            raw = INFO.get(label, {})
            name = label.replace("___", " - ").replace("_", " ").title()
            results.append({
                "name": name,
                "score": float(preds[i] * 100),
                "severity": raw.get("severity", "Medium"),
                "solution": raw.get("solution", ["Contact specialist."]),
                "cause": raw.get("cause", "Cause unknown.")
            })
    return results

# =======================
# 4. UI STRUCTURE
# =======================

# --- HERO HEADER ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; position: relative; z-index: 1;">
    <h1 class="glowing-text">LEAFGUARD AI</h1>
    <p style="color: #A0CFA0; font-size: 1.2rem; letter-spacing: 4px; margin-top: -10px;">
        BIO-DIGITAL PLANT DIAGNOSTICS SYSTEM
    </p>
</div>
""", unsafe_allow_html=True)

if "analysis" not in st.session_state: st.session_state.analysis = None

col1, col2 = st.columns([1, 1.4], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #39FF14;">🧬 SCAN INTERFACE</h3>', unsafe_allow_html=True)
    
    # Upload Area
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size: 50px; margin-bottom: 10px;">📸</div>
        <div style="color: #fff;">
            <b>UPLOAD PLANT SAMPLE</b><br>
            <span style="font-size: 0.8rem; color: #888;">AI Analysis Sequence</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(img, use_container_width=True, caption="Sample Acquired")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INITIATE DIAGNOSIS"):
            with st.spinner("ANALYZING BIO-DATA..."):
                time.sleep(1.5)
                results = get_prediction(img, model)
                if results:
                    st.session_state.analysis = results

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.analysis:
        top = st.session_state.analysis[0]
        others = st.session_state.analysis[1:]
        
        is_safe = "healthy" in top['name'].lower()
        # Màu sắc động dựa trên kết quả
        accent_color = "#39FF14" if is_safe else ("#FF0055" if top['severity'] == "High" else "#FFD700")
        status_msg = "HEALTHY SPECIMEN" if is_safe else "INFECTION DETECTED"

        st.markdown(f'<div class="glass-card" style="border-top: 4px solid {accent_color};">', unsafe_allow_html=True)
        
        # Result Header with SVG Circle Chart
        c_res1, c_res2 = st.columns([2, 1])
        with c_res1:
            st.markdown(f'<div style="color: {accent_color}; font-weight: 700; letter-spacing: 2px;">STATUS: {status_msg}</div>', unsafe_allow_html=True)
            st.markdown(f'<h2 style="font-size: 2.5rem; margin: 5px 0; color: #fff; text-shadow: 0 0 10px {accent_color};">{top["name"]}</h2>', unsafe_allow_html=True)
        with c_res2:
            # SVG Circular Chart Implementation
            score = top['score']
            dash_array = f"{score}, 100"
            st.markdown(f"""
            <div class="progress-container">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg"
                        d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path class="circle"
                        stroke="{accent_color}"
                        stroke-dasharray="{dash_array}"
                        d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <text x="18" y="20.35" class="percentage-text">{score:.0f}%</text>
                    <text x="18" y="27" class="label-text">MATCH</text>
                </svg>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Tabs
        t1, t2, t3 = st.tabs(["📊 DATA", "💊 PROTOCOL", "🧬 ORIGIN"])
        
        with t1: # Visualization
            st.markdown("<br>", unsafe_allow_html=True)
            for item in st.session_state.analysis:
                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #E0FFE0;">
                        <span>{item['name']}</span>
                        <span>{item['score']:.1f}%</span>
                    </div>
                    <div style="width: 100%; background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; margin-top: 4px;">
                        <div style="width: {item['score']}%; background: {accent_color}; height: 6px; border-radius: 4px; box-shadow: 0 0 8px {accent_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with t2: # Solution
            st.markdown("<br>", unsafe_allow_html=True)
            if is_safe:
                st.markdown(f'<div class="info-box" style="border-left-color: {accent_color}; color: #E0FFE0;">✅ Plant is in optimal health. No action required.</div>', unsafe_allow_html=True)
            else:
                for idx, sol in enumerate(top['solution'], 1):
                    st.markdown(f"""
                    <div style="display: flex; gap: 15px; margin-bottom: 15px; align-items: start;">
                        <div style="background: {accent_color}; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">{idx}</div>
                        <div style="color: #F0FFF0; line-height: 1.5;">{sol}</div>
                    </div>
                    """, unsafe_allow_html=True)

        with t3: # Cause
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-box">
                <strong style="color: {accent_color}; display: block; margin-bottom: 8px;">PATHOGEN PROFILE:</strong>
                {top['cause']}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Placeholder
        st.markdown("""
        <div class="glass-card" style="height: 450px; display: flex; align-items: center; justify-content: center; text-align: center; border: 1px dashed rgba(57, 255, 20, 0.2);">
            <div>
                <div style="font-size: 80px; opacity: 0.2; margin-bottom: 20px;">🌿</div>
                <h3 style="color: rgba(57, 255, 20, 0.5);">WAITING FOR BIO-SAMPLE</h3>
                <p style="color: rgba(255,255,255,0.3);">Upload image to activate scanner</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; opacity: 0.4; font-size: 0.7rem; color: #fff;">
    LEAFGUARD AI v3.0 • BIO-DIGITAL INTERFACE
</div>
""", unsafe_allow_html=True)
=======
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
