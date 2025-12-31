import os
import streamlit as st
import numpy as np
from PIL import Image
from src.auth_manager import AuthManager
from database.firestore_manager import FirestoreManager
from src.utils import save_diagnosis_image, process_label, get_plant_type_from_label
from database.db_operations import save_diagnosis as save_diagnosis_mysql, update_statistics


# Handle diagnosis
def handle_diagnosis(
    image: Image.Image,
    file,
    preds: np.ndarray,
    class_names: list,
    auth_manager: AuthManager,
    firestore: FirestoreManager,
    silent: bool = False  # If True, don't display messages, just return result
):
    CONFIDENCE_THRESHOLD_LOW = 40.0
    CONFIDENCE_THRESHOLD_HIGH = 60.0
   
    class_idx = np.argmax(preds)
    confidence = float(preds[class_idx] * 100)
    raw_label = class_names[class_idx]
   
    # Check confidence threshold
    if confidence < CONFIDENCE_THRESHOLD_LOW:
        if not silent:
            st.error("ĐỘ TIN CẬY QUÁ THẤP / KHÔNG THỂ XÁC ĐỊNH")
            st.write(f"AI chỉ tự tin **{confidence:.2f}%**. Đây có thể không phải ảnh lá cây hoặc ảnh quá mờ.")
            st.info("Gợi ý: Vui lòng chụp ảnh rõ hơn hoặc đến gần lá cây hơn.")
            st.subheader("Kết quả 'Nghi ngờ' của AI")
        return None
   
    show_warning = confidence < CONFIDENCE_THRESHOLD_HIGH
   
    # Process label
    plant_name, disease_name = process_label(raw_label)
    is_healthy = "healthy" in disease_name.lower() or "khỏe mạnh" in disease_name.lower()
   
    if show_warning and not silent:
        st.warning(f"Độ tin cậy trung bình ({confidence:.2f}%). Kết quả có thể không chính xác hoàn toàn.")
   
    # Create dictionary predictions for all classes
    predictions_dict = {class_names[i]: float(preds[i]) for i in range(len(class_names))}
   
    top_plant_type = get_plant_type_from_label(raw_label)
   
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
   
    top3_predictions = []
    for idx, class_name, conf in top3_filtered:
        plant_name_vn, disease_name_vn = process_label(class_name)
        lbl = f"{plant_name_vn} - {disease_name_vn}"
        top3_predictions.append({
            'label': lbl,
            'confidence': float(conf)
        })
       
    if auth_manager.is_logged_in():
        user_id = auth_manager.get_current_user_id()
       
        # Save image to directory
        image_path = save_diagnosis_image(image, user_id, file.name)
       
        # Lưu vào Firestore
        if not silent:
            with st.spinner("Đang lưu kết quả vào lịch sử..."):
                try:
                    diagnosis_id_firestore = firestore.save_diagnosis(
                        user_id=user_id,
                        plant_type=plant_name,
                        disease=disease_name,
                        confidence=float(confidence),
                        top3_predictions=top3_predictions
                    )
                except Exception as e:
                    st.warning(f"⚠️ Lỗi Firestore: {str(e)}")
        else:
            try:
                firestore.save_diagnosis(
                    user_id=user_id,
                    plant_type=plant_name,
                    disease=disease_name,
                    confidence=float(confidence),
                    top3_predictions=top3_predictions
                )
            except Exception as e:
                pass  # Silent mode
       
        # Save to MySQL (with image path)
        try:
            diagnosis_id_mysql = save_diagnosis_mysql(
                plant_type=plant_name,
                disease_status=disease_name,
                confidence=float(confidence / 100.0),  # Convert to Python float
                predictions=predictions_dict,
                firebase_user_id=user_id,
                image_path=image_path
            )
           
            if diagnosis_id_mysql:
                # Cập nhật thống kê
                update_statistics()
        except Exception as e:
            if not silent:
                st.warning(f"MySQL database error: {str(e)}")
   
    # Return kết quả để hiển thị
    return plant_name, disease_name, confidence, is_healthy