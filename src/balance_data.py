import os
import json
import sys


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
                       if f.lower().endswith(('.png', '.jpg', '.jpeg')) 
                       and not f.startswith('aug_')]  # Bỏ qua file đã được augment trước đó
        counts[cls] = len(valid_images)
   
    total_samples = sum(counts.values())
    num_classes = len(classes)
    max_count = max(counts.values())
    min_count = min(counts.values())
    
    print(f"\n📊 THỐNG KÊ DỮ LIỆU:")
    print(f"   - Tổng số class: {num_classes}")
    print(f"   - Tổng số ảnh: {total_samples}")
    print(f"   - Class nhiều nhất: {max_count} ảnh")
    print(f"   - Class ít nhất: {min_count} ảnh")
    print(f"   - Tỷ lệ chênh lệch: {max_count/min_count:.2f}x")
    
    # --- 3. TÍNH CLASS WEIGHTS ---
    # Có 2 công thức phổ biến:
    # 1. "balanced" (sklearn style): weight_i = total_samples / (num_classes * samples_in_class_i)
    #    -> Đảm bảo tổng weight của mỗi class bằng nhau
    # 2. "simple": weight_i = max_count / count_i
    #    -> Đơn giản hơn, class ít nhất có weight = max_count/min_count
    
    # Với imbalanced data nghiêm trọng (21x), nên dùng "balanced" để tránh weight quá lớn
    class_weights = {}
    
    print(f"\n⚖️  ĐANG TÍNH CLASS WEIGHTS (công thức 'balanced')...")
    print(f"   Công thức: weight = total_samples / (num_classes × samples_in_class)")
    
    for cls, count in sorted(counts.items()):
        # Dùng công thức "balanced" (chuẩn sklearn) - tốt hơn cho imbalanced data nghiêm trọng
        # Công thức này đảm bảo tổng weight của mỗi class gần bằng nhau
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
    
    print(f"\n✅ HOÀN TẤT! Class weights đã được lưu vào: {weights_file}")
    print(f"\n📈 THỐNG KÊ CLASS WEIGHTS:")
    print(f"   - Weight nhỏ nhất: {min_weight:.3f} (class nhiều dữ liệu nhất)")
    print(f"   - Weight lớn nhất: {max_weight:.3f} (class ít dữ liệu nhất)")
    print(f"   - Tỷ lệ weight: {max_weight/min_weight:.2f}x")
    print(f"\n💡 HƯỚNG DẪN SỬ DỤNG:")
    print(f"   1. Class weights sẽ được tự động load trong data_loader.py")
    print(f"   2. Truyền vào model.fit(class_weight=class_weights) khi training")
    print(f"   3. Model sẽ tự động ưu tiên các class ít dữ liệu trong quá trình học")
    print(f"   4. KHÔNG cần copy file, dataset giữ nguyên kích thước!")
    print(f"\n🎯 GIẢI THÍCH:")
    print(f"   - Class ít dữ liệu có weight CAO → Loss được nhân với weight lớn")
    print(f"   - Model sẽ học tốt hơn các class hiếm gặp (bệnh hiếm)")
    print(f"   - Kết hợp với Data Augmentation → Hiệu quả tối ưu")
    
    return class_weights


def get_class_weights_dict(train_dir, class_indices):
    """
    Chuyển đổi class weights từ tên class sang class index để dùng trong model.fit()
    
    Args:
        train_dir: Đường dẫn đến thư mục train
        class_indices: Dictionary từ train_gen.class_indices {class_name: index}
    
    Returns:
        dict: {class_index: weight} để truyền vào model.fit(class_weight=...)
    """
    weights_file = os.path.join(os.path.dirname(train_dir), "class_weights.json")
    
    if not os.path.exists(weights_file):
        print(f"⚠️  Chưa có file class_weights.json. Đang tính toán...")
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
   
    # Tính toán và lưu class weights (KHÔNG copy file)
    calculate_class_weights(path_to_train)