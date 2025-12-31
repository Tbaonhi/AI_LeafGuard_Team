import streamlit as st
import random
from src.auth_manager import AuthManager
from database.firestore_manager import FirestoreManager
from src.utils import get_solution


#Inject bio-digital theme CSS
def inject_theme_css():
    """Inject bio-digital theme CSS"""
    st.markdown("""
    <style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Outfit:wght@300;400;600&display=swap');


    :root {
        --neon-green: #39FF14;
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


    /* ANIMATED JUNGLE BACKGROUND */
    div[data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 50%, #0a2e1e 0%, #000000 100%);
        background-size: 100% 100%;
        color: var(--text-primary);
    }


    /* FALLING LEAVES ANIMATION */
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


    /* GLOWING TEXT */
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


    /* GLASS CARDS */
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


    /* CIRCULAR PROGRESS */
    .progress-container {
        position: relative;
        width: 150px;
        height: 150px;
        margin-left: auto;
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
        stroke-width: 2.5;
    }


    .circle {
        fill: none;
        stroke-width: 2.5;
        stroke-linecap: round;
        animation: progress 1s ease-out forwards;
        transform-origin: center;
        transform: rotate(-90deg);
    }


    .percentage-text {
        fill: #fff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: bold;
        font-size: 0.5em;
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


    /* Camera Input Styling */
    div[data-testid="stCameraInput"] {
        border: 2px solid rgba(57, 255, 20, 0.5) !important;
        border-radius: 16px !important;
        padding: 10px !important;
        background: rgba(0, 0, 0, 0.3) !important;
        box-shadow: 0 0 20px rgba(57, 255, 20, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stCameraInput"]:hover {
        border-color: var(--neon-green) !important;
        box-shadow: 0 0 30px rgba(57, 255, 20, 0.4) !important;
    }
    div[data-testid="stCameraInput"] video {
        border-radius: 12px !important;
    }


    /* File Uploader Styling */
    div[data-testid="stFileUploader"] {
        border: 2px dashed rgba(57, 255, 20, 0.4) !important;
        border-radius: 16px !important;
        background: rgba(0, 0, 0, 0.2) !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: var(--neon-green) !important;
        background: rgba(57, 255, 20, 0.1) !important;
        box-shadow: 0 0 20px rgba(57, 255, 20, 0.2) !important;
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


def inject_falling_leaves():
    """Inject falling leaves animation"""
    leaves_html = ""
    for i in range(15):
        left = random.randint(0, 100)
        delay = random.uniform(0, 10)
        duration = random.uniform(10, 20)
        icon = random.choice(["🌿", "🍃", "🍂", "☘️"])
        leaves_html += f'<div class="leaf" style="left: {left}%; animation-delay: {delay}s; animation-duration: {duration}s;">{icon}</div>'
    st.markdown(leaves_html, unsafe_allow_html=True)


def render_hero_header():
    """Render hero header with glowing text"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px; position: relative; z-index: 1;">
        <h1 class="glowing-text">LEAFGUARD AI</h1>
        <p style="color: #A0CFA0; font-size: 1.2rem; letter-spacing: 4px; margin-top: -10px;">
            BIO-DIGITAL PLANT DIAGNOSTICS SYSTEM
        </p>
    </div>
    """, unsafe_allow_html=True)


# Render sidebar
def render_sidebar(auth_manager: AuthManager, firestore: FirestoreManager):
    with st.sidebar:
        # User dropdown menu với icon
        with st.expander("Trạng thái đăng nhập", expanded=False):
            if auth_manager.is_logged_in():
                st.success("Bạn đã đăng nhập, có thể xem lịch sử chẩn đoán và thống kê")
            else:
                st.info("Vui lòng đăng nhập để lưu lịch sử chẩn đoán")
# Get confidence level description
def get_confidence_level(confidence: float) -> str:
    """Convert numeric confidence to human-readable level"""
    if confidence >= 80:
        return "Kết quả rất đáng tin cậy. Bạn có thể yên tâm áp dụng các biện pháp điều trị."
    elif confidence >= 60:
        return "Bạn nên tham khảo ý kiến của các chuyên gia để chữa bệnh cho cây kịp thời."
    elif confidence >= 40:
        return "Kết quả có thể không chính xác hoàn toàn. Bạn nên chụp ảnh rõ hơn hoặc tham khảo ý kiến của các chuyên gia để chữa bệnh cho cây."
    else:
        return "Tôi chưa chắc chắn. Bạn nên chụp ảnh rõ hơn hoặc tham khảo ý kiến của các chuyên gia để chữa bệnh cho cây."


# Render diagnosis result with new styling
def render_diagnosis_result(plant_name: str, disease_name: str, confidence: float, is_healthy: bool, raw_label: str = None):
    """Render diagnosis result with bio-digital styling"""
    # Determine accent color
    accent_color = "#39FF14" if is_healthy else ("#FF0055" if confidence < 60 else "#FFD700")
    status_msg = "KHỎE MẠNH" if is_healthy else "PHÁT HIỆN BỆNH"
   
    st.markdown(f'<div class="glass-card" style="border-top: 4px solid {accent_color};">', unsafe_allow_html=True)
   
    # Result Header with SVG Circle Chart
    c_res1, c_res2 = st.columns([2, 1])
    with c_res1:
        st.markdown(f'<div style="color: {accent_color}; font-weight: 700; letter-spacing: 2px; font-size: 0.9rem;">TRẠNG THÁI: {status_msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="font-size: 2rem; margin: 5px 0; color: #fff; text-shadow: 0 0 10px {accent_color};">{plant_name}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 1.2rem; color: #A0CFA0; margin-top: -5px;">{disease_name}</p>', unsafe_allow_html=True)
    with c_res2:
        # SVG Circular Chart
        dash_array = f"{confidence}, 100"
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
                <text x="18" y="20.35" class="percentage-text">{confidence:.0f}%</text>
                <text x="18" y="27" class="label-text">ĐỘ TIN CẬY</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)
   
    # Confidence description
    confidence_desc = get_confidence_level(confidence)
    st.markdown(f'<div class="info-box" style="border-left-color: {accent_color}; margin-top: 15px;">{confidence_desc}</div>', unsafe_allow_html=True)
   
    st.divider()
   
    # Render solution if available
    if raw_label:
        render_solution(raw_label, is_healthy, accent_color)
   
    st.markdown('</div>', unsafe_allow_html=True)




# Render solution (cause and treatment) with new styling
def render_solution(raw_label: str, is_healthy: bool, accent_color: str = "#39FF14"):
    """Render solution information with bio-digital styling"""
    solution = get_solution(raw_label)
   
    if not solution:
        return
   
    # Tabs for organized display - Thứ tự: Dấu hiệu | Nguyên Nhân | Điều Trị | Phòng ngừa
    t1, t2, t3, t4 = st.tabs(["🔬 DẤU HIỆU", "🧬 NGUYÊN NHÂN", "💊 ĐIỀU TRỊ", "🛡️ PHÒNG NGỪA"])
   
    with t1:  # Symptoms
        st.markdown("<br>", unsafe_allow_html=True)
        if solution.get('symptoms') and isinstance(solution['symptoms'], list):
            st.markdown(f'<div style="color: {accent_color}; font-weight: 700; margin-bottom: 15px;">TẠI SAO TÔI KHẲNG ĐỊNH ĐÂY LÀ BỆNH NÀY?</div>', unsafe_allow_html=True)
            for symptom in solution['symptoms']:
                st.markdown(f"""
                <div style="display: flex; gap: 15px; margin-bottom: 12px; align-items: start;">
                    <div style="background: {accent_color}; color: #000; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; font-size: 0.7rem;">•</div>
                    <div style="color: #F0FFF0; line-height: 1.6;">{symptom}</div>
                </div>
                """, unsafe_allow_html=True)
       
        if solution.get('why_this_disease'):
            st.markdown(f'<div class="info-box" style="border-left-color: {accent_color}; margin-top: 20px;">{solution["why_this_disease"]}</div>', unsafe_allow_html=True)
   
    with t2:  # Cause
        st.markdown("<br>", unsafe_allow_html=True)
        if solution.get('cause'):
            st.markdown(f"""
            <div class="info-box">
                <strong style="color: {accent_color}; display: block; margin-bottom: 8px;">NGUYÊN NHÂN:</strong>
                {solution['cause']}
            </div>
            """, unsafe_allow_html=True)
           
            if solution.get('conditions'):
                st.markdown(f"""
                <div class="info-box" style="margin-top: 15px;">
                    <strong style="color: {accent_color}; display: block; margin-bottom: 8px;">ĐIỀU KIỆN PHÁT TRIỂN:</strong>
                    {solution['conditions']}
                </div>
                """, unsafe_allow_html=True)
   
    with t3:  # Treatment
        st.markdown("<br>", unsafe_allow_html=True)
        if is_healthy:
            st.markdown(f'<div class="info-box" style="border-left-color: {accent_color};">✅ Cây trồng đang phát triển tốt. Không cần điều trị.</div>', unsafe_allow_html=True)
        else:
            if solution.get('treatment') and isinstance(solution['treatment'], list):
                st.markdown(f'<div style="color: {accent_color}; font-weight: 700; margin-bottom: 15px;">BIỆN PHÁP CANH TÁC (XỬ LÝ NGAY):</div>', unsafe_allow_html=True)
                for idx, treatment in enumerate(solution['treatment'], 1):
                    st.markdown(f"""
                    <div style="display: flex; gap: 15px; margin-bottom: 15px; align-items: start;">
                        <div style="background: {accent_color}; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">{idx}</div>
                        <div style="color: #F0FFF0; line-height: 1.6;">{treatment}</div>
                    </div>
                    """, unsafe_allow_html=True)
   
    with t4:  # Prevention
        st.markdown("<br>", unsafe_allow_html=True)
        if solution.get('prevention') and isinstance(solution['prevention'], list):
            for i, prevention in enumerate(solution['prevention'], 1):
                st.markdown(f"""
                <div style="display: flex; gap: 15px; margin-bottom: 12px; align-items: start;">
                    <div style="background: {accent_color}; color: #000; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">{i}</div>
                    <div style="color: #F0FFF0; line-height: 1.6;">{prevention}</div>
                </div>
                """, unsafe_allow_html=True)




# Render top 3 predictions with new styling
def render_top3_predictions(preds, class_names, top_plant_type=None, accent_color: str = "#39FF14"):
    from src.utils import get_plant_type_from_label, process_label
   
    # Collect predictions first
    predictions_to_show = []
   
    if top_plant_type:
        filtered_predictions = []
        for i, class_name in enumerate(class_names):
            plant_type = get_plant_type_from_label(class_name)
            conf = preds[i] * 100
            if plant_type == top_plant_type and conf >= 40.0:
                filtered_predictions.append((i, class_name, conf))
       
        filtered_predictions.sort(key=lambda x: x[2], reverse=True)
        top3_filtered = filtered_predictions[:3]
       
        if len(top3_filtered) == 0:
            same_plant_predictions = [(i, class_names[i], preds[i] * 100)
                                      for i in range(len(class_names))
                                      if get_plant_type_from_label(class_names[i]) == top_plant_type]
            same_plant_predictions.sort(key=lambda x: x[2], reverse=True)
            top3_filtered = same_plant_predictions[:3]
       
        predictions_to_show = top3_filtered
    else:
        # Fallback: show top 3 without filtering
        top3_idx = preds.argsort()[-3:][::-1]
        predictions_to_show = [(i, class_names[i], preds[i] * 100) for i in top3_idx]
   
    # Only render if we have predictions to show
    if predictions_to_show:
        st.markdown(f'<h3 style="color: {accent_color}; margin-bottom: 20px;">CHI TIẾT XÁC SUẤT</h3>', unsafe_allow_html=True)
       
        for idx, class_name, prob in predictions_to_show:
            plant_name, disease_name = process_label(class_name)
            lbl = f"{plant_name} - {disease_name}"
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: #E0FFE0; margin-bottom: 5px;">
                    <span>{lbl}</span>
                    <span style="color: {accent_color}; font-weight: bold;">{prob:.1f}%</span>
                </div>
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px;">
                    <div style="width: {prob}%; background: {accent_color}; height: 6px; border-radius: 4px; box-shadow: 0 0 8px {accent_color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)