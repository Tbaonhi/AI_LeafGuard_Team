import os
import json
import sys
import shutil
from PIL import Image
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator




def calculate_class_weights(train_dir):
    # --- 1. KIỂM TRA AN TOÀN ---
    if not os.path.exists(train_dir):
        print(f"LỖI: Không tìm thấy thư mục '{train_dir}'")
        return None


    print(f"Đang phân tích cân bằng dữ liệu tại: {train_dir}")
   
    # --- 2. ĐẾM SỐ ẢNH ---
    counts = {}
    # Chỉ lấy tên các thư mục con (các class bệnh)
    classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
   
    if not classes:
        print("Lỗi: Thư mục rỗng, không có class nào!")
        return None


    for cls in classes:
        cls_path = os.path.join(train_dir, cls)
        # Chỉ đếm file ảnh, bỏ qua file hệ thống rác nếu có
        valid_images = [f for f in os.listdir(cls_path)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.jfif'))
                       and not f.startswith('aug_')]  # Bỏ qua file đã được augment trước đó
        counts[cls] = len(valid_images)
   
    total_samples = sum(counts.values())
    num_classes = len(classes)
    max_count = max(counts.values())
    min_count = min(counts.values())
   
    print(f"\nTHỐNG KÊ DỮ LIỆU:")
    print(f"   - Tổng số class: {num_classes}")
    print(f"   - Tổng số ảnh: {total_samples}")
    print(f"   - Class nhiều nhất: {max_count} ảnh")
    print(f"   - Class ít nhất: {min_count} ảnh")
    print(f"   - Tỷ lệ chênh lệch: {max_count/min_count:.2f}x")
   
    # --- 3. TÍNH CLASS WEIGHTS ---
    class_weights = {}
   
    print(f"\nĐANG TÍNH CLASS WEIGHTS (công thức 'balanced')...")
    print(f"   Công thức: weight = total_samples / (num_classes × samples_in_class)")
   
    for cls, count in sorted(counts.items()):
        # Dùng công thức "balanced" (chuẩn sklearn)
        weight_balanced = total_samples / (num_classes * count) if count > 0 else 1.0
       
        class_weights[cls] = weight_balanced
       
        # Tính thêm weight đơn giản để so sánh
        weight_simple = max_count / count if count > 0 else 1.0
        print(f"   {cls:40s}: {count:4d} ảnh -> balanced={weight_balanced:.3f} (simple={weight_simple:.3f})")
   
    # Lưu class weights vào file JSON để dùng sau
    weights_file = os.path.join(os.path.dirname(train_dir), "class_weights.json")
    with open(weights_file, 'w', encoding='utf-8') as f:
        json.dump(class_weights, f, indent=2, ensure_ascii=False)
   
    # Tính toán thống kê về weights
    weights_list = list(class_weights.values())
    min_weight = min(weights_list)
    max_weight = max(weights_list)
   
    print(f"\nHOÀN TẤT! Class weights đã được lưu vào: {weights_file}")
    print(f"\nTHỐNG KÊ CLASS WEIGHTS:")
    print(f"   - Weight nhỏ nhất: {min_weight:.3f} (class nhiều dữ liệu nhất)")
    print(f"   - Weight lớn nhất: {max_weight:.3f} (class ít dữ liệu nhất)")
    print(f"   - Tỷ lệ weight: {max_weight/min_weight:.2f}x")
   
    return class_weights




def oversample_data(train_dir, multiplier=2.5):
    """
    Oversampling các class có ít ảnh lên gấp multiplier lần (mặc định 2.5x)
    Không oversample bằng số lượng lớn nhất, chỉ tăng gấp 2-3 lần để tránh train vặt
   
    Args:
        train_dir: Đường dẫn đến thư mục train
        multiplier: Hệ số nhân (2.0 = gấp 2, 2.5 = gấp 2.5, 3.0 = gấp 3)
    """
    if not os.path.exists(train_dir):
        print(f"LỖI: Không tìm thấy thư mục '{train_dir}'")
        return False
   
    print(f"\nBẮT ĐẦU OVERSAMPLING (hệ số: {multiplier}x)...")
    print(f"   Chỉ oversample các class có ít ảnh, không oversample bằng số lượng lớn nhất")
   
    # Đếm số ảnh mỗi class
    counts = {}
    classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
   
    for cls in classes:
        cls_path = os.path.join(train_dir, cls)
        valid_images = [f for f in os.listdir(cls_path)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.jfif'))
                       and not f.startswith('aug_')]
        counts[cls] = len(valid_images)
   
    if not counts:
        print("Lỗi: Không tìm thấy ảnh nào!")
        return False
   
    # Tính ngưỡng: chỉ oversample các class có số lượng < trung bình
    avg_count = sum(counts.values()) / len(counts)
    threshold = avg_count * 0.7  # Chỉ oversample các class < 70% trung bình
   
    print(f"\nTHỐNG KÊ:")
    print(f"   - Số lượng trung bình: {avg_count:.0f} ảnh/class")
    print(f"   - Ngưỡng oversampling: {threshold:.0f} ảnh (các class < ngưỡng sẽ được oversample)")
   
    # Tạo ImageDataGenerator cho augmentation
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
   
    total_augmented = 0
   
    for cls, count in sorted(counts.items()):
        if count >= threshold:
            print(f"   {cls:40s}: {count:4d} ảnh -> Bỏ qua (đủ dữ liệu)")
            continue
       
        # Tính số ảnh cần tạo thêm
        target_count = int(count * multiplier)
        needed = target_count - count
       
        if needed <= 0:
            print(f"   {cls:40s}: {count:4d} ảnh -> Đã đủ")
            continue
       
        print(f"   {cls:40s}: {count:4d} ảnh -> Tạo thêm {needed} ảnh (target: {target_count})")
       
        cls_path = os.path.join(train_dir, cls)
        image_files = [f for f in os.listdir(cls_path)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.jfif'))
                      and not f.startswith('aug_')]
       
        # Tạo ảnh augmented
        created = 0
        file_idx = 0
       
        while created < needed and image_files:
            # Lấy ảnh để augment
            img_file = image_files[file_idx % len(image_files)]
            img_path = os.path.join(cls_path, img_file)
           
            try:
                # Load và augment ảnh
                img = Image.open(img_path).convert('RGB')
                img_array = np.array(img)
                img_array = img_array.reshape((1,) + img_array.shape)
               
                # Tạo ảnh augmented
                aug_iter = datagen.flow(img_array, batch_size=1)
                aug_img = next(aug_iter)[0].astype('uint8')
               
                # Lưu ảnh mới
                aug_filename = f"aug_{created:04d}_{img_file}"
                aug_path = os.path.join(cls_path, aug_filename)
               
                aug_pil = Image.fromarray(aug_img)
                aug_pil.save(aug_path, quality=95)
               
                created += 1
                total_augmented += 1
               
            except Exception as e:
                print(f"      Lỗi khi augment {img_file}: {str(e)}")
           
            file_idx += 1
       
        print(f"      Đã tạo {created} ảnh mới cho class {cls}")
   
    print(f"\nHOÀN TẤT OVERSAMPLING!")
    print(f"   - Tổng số ảnh đã tạo: {total_augmented}")
    print(f"   - Dataset đã được cân bằng tốt hơn, sẵn sàng để train")
   
    return True




def get_class_weights_dict(train_dir, class_indices):
    weights_file = os.path.join(os.path.dirname(train_dir), "class_weights.json")
   
    if not os.path.exists(weights_file):
        print(f"Chưa có file class_weights.json. Đang tính toán...")
        class_weights_by_name = calculate_class_weights(train_dir)
        if class_weights_by_name is None:
            return None
    else:
        with open(weights_file, 'r', encoding='utf-8') as f:
            class_weights_by_name = json.load(f)
   
    # Chuyển đổi từ tên class sang index
    class_weights_by_index = {}
    for class_name, weight in class_weights_by_name.items():
        if class_name in class_indices:
            class_weights_by_index[class_indices[class_name]] = weight
   
    return class_weights_by_index




# --- PHẦN CHẠY CHÍNH ---
if __name__ == "__main__":
    # dataset_final được tạo ra từ file split_data.py
    path_to_train = "dataset/train"
   
    # Bước 1: Oversampling (tăng số lượng ảnh cho các class ít dữ liệu)
    print("=" * 60)
    print("BƯỚC 1: OVERSAMPLING DỮ LIỆU")
    print("=" * 60)
    oversample_data(path_to_train, multiplier=2.5)
   
    # Bước 2: Tính toán class weights
    print("\n" + "=" * 60)
    print("BƯỚC 2: TÍNH TOÁN CLASS WEIGHTS")
    print("=" * 60)
    calculate_class_weights(path_to_train)

