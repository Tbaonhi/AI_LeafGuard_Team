import os
from datetime import datetime
from PIL import Image
import streamlit as st


# Save diagnosis image to directory
def save_diagnosis_image(image: Image.Image, user_id: str, original_filename: str) -> str:
    try:
        # Create uploads/diagnoses directory if not exists
        upload_dir = f"uploads/diagnoses/{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
       
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(original_filename)[1] or ".jpg"
        filename = f"{timestamp}_{original_filename}"
       
        # Full path
        file_path = os.path.join(upload_dir, filename)
       
        # Save image
        image.save(file_path, quality=95)
       
        # Return relative path
        image_path = file_path.replace("\\", "/")  # Normalize path cho cross-platform
       
        return image_path
       
    except Exception as e:
        st.warning(f"⚠️ Lỗi lưu ảnh: {str(e)}")
        return None


# Plant name mapping to Vietnamese
PLANT_NAME_MAPPING = {
    "Pepper": "Ớt chuông",
    "Potato": "Khoai tây",
    "Tomato": "Cà chua"
}


# Disease name mapping to Vietnamese
# Mapping đầy đủ cho tất cả các format có thể có
# Lưu ý: Tất cả keys đều dùng single underscore để dễ match
DISEASE_NAME_MAPPING = {
    # Basic disease names
    "Bacterial_spot": "Bệnh đốm vi khuẩn",
    "Early_blight": "Bệnh đốm vòng (bệnh cháy sớm)",
    "Late_blight": "Bệnh mốc sương (bệnh cháy muộn)",
    "Leaf_Mold": "Bệnh nấm mốc lá",
    "Septoria_leaf_spot": "Bệnh đốm lá Septoria (Đốm mắt cua)",
    "Spider_mites_Two_spotted_spider_mite": "Nhện đỏ 2 chấm (Nhện chăng tơ)",
    "Target_Spot": "Bệnh đốm đích",
    "Tomato_YellowLeaf_Curl_Virus": "Bệnh virus xoăn vàng lá",  # Normalized từ Tomato_YellowLeaf__Curl_Virus
    "Tomato_mosaic_virus": "Bệnh virus khảm",
    "healthy": "Cây khỏe mạnh",
    # Pepper specific (có bell prefix)
    "bell_Bacterial_spot": "Bệnh đốm vi khuẩn (bệnh héo xanh vi khuẩn)",
    "bell_healthy": "Cây khỏe mạnh",
    # Tomato specific (có Tomato prefix trong tên bệnh)
    "Tomato_Target_Spot": "Bệnh đốm đích (Đốm vòng Corynespora)",
    "Tomato_Tomato_YellowLeaf_Curl_Virus": "Bệnh virus xoăn vàng lá",  # Normalized
    "Tomato_Tomato_mosaic_virus": "Bệnh virus khảm"
}


# Process label and translate to Vietnamese
def process_label(raw_label: str) -> tuple[str, str]:
    """
    Process label và translate sang tiếng Việt
    Xử lý các format: Pepper__bell___Bacterial_spot, Potato___Early_blight, Tomato_Bacterial_spot
    """
    # Normalize: thay tất cả multiple underscores thành single underscore
    # Xử lý cả __ và ___
    import re
    clean_label = re.sub(r'_+', '_', raw_label)  # Thay tất cả _+ thành _
    clean_label = clean_label.strip('_')  # Xóa _ ở đầu và cuối
   
    # Split by underscore
    parts = [p for p in clean_label.split('_') if p]  # Loại bỏ empty strings
   
    if not parts:
        return "Không xác định", "Không xác định"
   
    # Get plant name from first part
    plant_name_en = parts[0]
    plant_name = PLANT_NAME_MAPPING.get(plant_name_en, plant_name_en)
   
    # Get disease name from remaining parts
    if len(parts) > 1:
        # Tạo disease name từ các parts còn lại (bỏ plant name đầu tiên)
        disease_name_en = "_".join(parts[1:])
       
        # Check if it's healthy
        if "healthy" in clean_label.lower() or disease_name_en.lower() == "healthy":
            disease_name = "Khỏe mạnh"
        else:
            # Thử map với toàn bộ disease name trước
            disease_name = DISEASE_NAME_MAPPING.get(disease_name_en)
           
            # Nếu không tìm thấy, thử bỏ các modifier như "bell", "Tomato" ở đầu
            if not disease_name:
                # Bỏ qua "bell" nếu có ở vị trí đầu tiên
                if len(parts) > 2 and parts[1].lower() == "bell":
                    disease_name_en_alt = "_".join(parts[2:])
                    disease_name = DISEASE_NAME_MAPPING.get(disease_name_en_alt)
               
                # Nếu vẫn không tìm thấy, thử bỏ "Tomato" nếu có ở vị trí đầu tiên
                if not disease_name and len(parts) > 2 and parts[1].lower() == "tomato":
                    disease_name_en_alt = "_".join(parts[2:])
                    disease_name = DISEASE_NAME_MAPPING.get(disease_name_en_alt)
                    # Nếu vẫn không có, thử với Tomato prefix
                    if not disease_name:
                        disease_name_en_alt = "_".join(parts[1:])
                        disease_name = DISEASE_NAME_MAPPING.get(disease_name_en_alt)
           
            # Nếu vẫn không tìm thấy, format đẹp hơn từ parts
            if not disease_name:
                # Bỏ qua "bell" modifier khi format
                display_parts = [p for p in parts[1:] if p.lower() != "bell"]
                if display_parts:
                    disease_name = " ".join(display_parts).replace("_", " ").title()
                else:
                    disease_name = "Không xác định"
    else:
        # Chỉ có plant name, không có disease
        if "healthy" in clean_label.lower():
            disease_name = "Khỏe mạnh"
        else:
            disease_name = "Không xác định"
   
    return plant_name, disease_name


# Get plant type from label (for filtering same plant type)
def get_plant_type_from_label(raw_label: str) -> str:
    """Extract plant type from label for filtering"""
    clean_label = raw_label.replace("___", "_")
    parts = clean_label.split("_")
    return parts[0] if parts else ""


# Load solutions from JSON file
@st.cache_data
def load_solutions():
    """Load solutions from solutions.json file"""
    import json
    solutions_path = "solutions.json"
    if not os.path.exists(solutions_path):
        return {}
    try:
        with open(solutions_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Không thể tải file solutions.json: {str(e)}")
        return {}


# Get solution for a given label
def get_solution(raw_label: str):
    """
    Get solution information for a given raw label
    Returns: dict with 'cause' and 'treatment' or None if not found
    """
    solutions = load_solutions()
    if not solutions:
        return None
   
    # Try exact match first
    if raw_label in solutions:
        return solutions[raw_label]
   
    # Try normalized match (handle different underscore patterns)
    import re
   
    # Normalize: replace multiple underscores with single underscore
    normalized_label = re.sub(r'_+', '_', raw_label).strip('_')
   
    # Try direct normalized match
    if normalized_label in solutions:
        return solutions[normalized_label]
   
    # Try matching with different underscore patterns
    # solutions.json uses format like "Pepper__bell___Bacterial_spot"
    parts = normalized_label.split('_')
   
    if len(parts) >= 2:
        # Try format: Plant___Disease
        triple_underscore = f"{parts[0]}___{'_'.join(parts[1:])}"
        if triple_underscore in solutions:
            return solutions[triple_underscore]
       
        # Try format: Plant__bell___Disease (for pepper)
        if len(parts) >= 3 and parts[1].lower() == 'bell':
            bell_format = f"{parts[0]}__bell___{'_'.join(parts[2:])}"
            if bell_format in solutions:
                return solutions[bell_format]
       
        # Try format: Plant___Tomato_Disease (for tomato with Tomato prefix)
        if len(parts) >= 3 and parts[1].lower() == 'tomato':
            tomato_format = f"{parts[0]}___{parts[1]}_{'_'.join(parts[2:])}"
            if tomato_format in solutions:
                return solutions[tomato_format]
   
    # Try matching Tomato virus formats with different naming conventions
    if "Tomato" in normalized_label:
        # Handle YellowLeaf vs Yellow_Leaf
        if "YellowLeaf" in normalized_label or "Yellow_Leaf" in normalized_label:
            # Try with triple underscores and Tomato prefix
            tomato_yellow_variants = [
                f"Tomato___Tomato_Yellow_Leaf_Curl_Virus",
                f"Tomato___Tomato_YellowLeaf__Curl_Virus",
                normalized_label.replace("YellowLeaf", "Yellow_Leaf"),
                normalized_label.replace("Yellow_Leaf", "YellowLeaf"),
            ]
            for variant in tomato_yellow_variants:
                # Try with different underscore patterns
                variant_triple = variant.replace("__", "___").replace("_", "___", 1) if "___" not in variant[:20] else variant
                if variant_triple in solutions:
                    return solutions[variant_triple]
                if variant in solutions:
                    return solutions[variant]
       
        # Handle Spider mites (has space in solutions.json)
        if "Spider" in normalized_label and "mite" in normalized_label.lower():
            spider_variants = [
                "Tomato___Spider_mites Two-spotted_spider_mite",
                normalized_label.replace("_", " ", 1) if "Two" in normalized_label else normalized_label,
            ]
            for variant in spider_variants:
                if variant in solutions:
                    return solutions[variant]
   
    # Try iterating through all solutions keys and find best match
    # This is a fallback for edge cases
    for key in solutions.keys():
        # Normalize both for comparison
        key_normalized = re.sub(r'_+', '_', key).strip('_').lower()
        label_normalized = normalized_label.lower()
       
        # Check if key contains all important parts of label
        key_parts = set(key_normalized.split('_'))
        label_parts = set(label_normalized.split('_'))
       
        # If most parts match, consider it a match
        if len(label_parts) > 0 and len(key_parts.intersection(label_parts)) >= len(label_parts) * 0.7:
            return solutions[key]
   
    return None