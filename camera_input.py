# camera_input.py
import streamlit as st
from PIL import Image

def get_image_input():
    """
    Trả về:
        image (PIL.Image) hoặc None
    """

    st.subheader("📤 Image Input")

    source = st.radio(
        "Choose image source:",
        ("Upload image", "Use camera"),
        key="image_source"
    )

    image = None

    if source == "Upload image":
        uploaded_file = st.file_uploader(
            "Supported formats: JPG, PNG, JPEG",
            type=["jpg", "png", "jpeg"],
            key="file_uploader"
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")

    elif source == "Use camera":
        camera_file = st.camera_input(
            "📷 Capture leaf image",
            key="camera_input"
        )
        if camera_file is not None:
            image = Image.open(camera_file).convert("RGB")

    return image
