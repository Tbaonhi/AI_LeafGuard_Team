# create_class_indices.py
import os
import json
import sys

# Sửa import để hoạt động cả khi chạy trực tiếp và khi import như module
try:
    from src.data_loader import create_generators
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.data_loader import create_generators

if __name__ == "__main__":
    print("--- Tạo file class_indices.json ---")
    
    # 1. Load data để lấy class_indices
    dataset_path = "dataset"
    if not os.path.exists(dataset_path):
        print(f"LỖI: Không tìm thấy thư mục '{dataset_path}'")
        exit()
    
    print(f"Đang load dữ liệu từ: {dataset_path}")
    train_gen, _, _ = create_generators(dataset_path)
    
    # 2. Lấy class_indices từ train generator
    class_indices = train_gen.class_indices
    print(f"Đã tìm thấy {len(class_indices)} classes")
    
    # 3. Tạo thư mục models nếu chưa có
    os.makedirs("models", exist_ok=True)
    
    # 4. Lưu vào file JSON
    output_path = "models/class_indices.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(class_indices, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Đã tạo file: {output_path}")
    print(f"\nDanh sách classes:")
    for class_name, index in sorted(class_indices.items(), key=lambda x: x[1]):
        print(f"  {index}: {class_name}")
