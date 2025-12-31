# camera_input.py
import streamlit as st
from PIL import Image


def get_image_input():
    # Radio buttons để chọn nguồn - gọn gàng hơn
    source = st.radio(
        "Chọn nguồn ảnh:",
        ("Tải ảnh lên", "Chụp từ camera"),
        key="image_source",
        horizontal=True
    )


    image = None
    uploaded_file = None


    if source == "Tải ảnh lên":
        # File uploader gọn gàng, không có card lớn
        uploaded_file = st.file_uploader(
            "Chọn file ảnh (JPG, PNG, JPEG, WEBP, JFIF)",
            type=["jpg", "png", "jpeg", "webp", "jfif"],
            key="file_uploader",
            help="Kéo thả file vào đây hoặc click để chọn"
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")


    elif source == "Chụp từ camera":
        # Camera input - styling đã được định nghĩa trong theme CSS
        camera_file = st.camera_input(
            "📷 Chụp ảnh lá cây",
            key="camera_input",
            help="Đặt lá cây vào khung và chụp ảnh. Đảm bảo ánh sáng đủ và lá cây rõ nét."
        )
        if camera_file is not None:
            image = Image.open(camera_file).convert("RGB")
            uploaded_file = camera_file  # Camera input cũng là file object


    return image, uploaded_file