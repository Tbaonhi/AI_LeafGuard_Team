import os
import shutil
import random
import sys


def balance_train_data(train_dir):
    # --- 1. KIỂM TRA AN TOÀN ---
    if not os.path.exists(train_dir):
        print(f"LỖI: Không tìm thấy thư mục '{train_dir}'")
        return


    print(f"Đang kiểm tra cân bằng dữ liệu tại: {train_dir}")
   
    # --- 2. ĐẾM SỐ ẢNH ---
    counts = {}
    # Chỉ lấy tên các thư mục con (các class bệnh)
    classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
   
    if not classes:
        print("Lỗi: Thư mục rỗng, không có class nào!")
        return


    for cls in classes:
        cls_path = os.path.join(train_dir, cls)
        # Chỉ đếm file ảnh, bỏ qua file hệ thống rác nếu có
        valid_images = [f for f in os.listdir(cls_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        counts[cls] = len(valid_images)
   
    max_count = max(counts.values())
    print(f"Class nhiều nhất có: {max_count} ảnh.")
    print("   -> Các class ít hơn sẽ được nhân bản (Oversampling) để bằng số này.")


    # --- 3. THỰC HIỆN OVERSAMPLING ---
    total_augmented = 0
   
    for cls, count in counts.items():
        if count < max_count:
            target_augment = max_count - count
            print(f"   Wait... Class '{cls}': {count} ảnh -> Cần thêm {target_augment} ảnh.")
           
            cls_path = os.path.join(train_dir, cls)
            files = [f for f in os.listdir(cls_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
           
            if not files:
                continue


            for i in range(target_augment):
                # Chọn ngẫu nhiên 1 ảnh gốc để copy
                random_file = random.choice(files)
                src = os.path.join(cls_path, random_file)
               
                # Đặt tên file mới: aug_sốthứtự_têncũ
                dst = os.path.join(cls_path, f"aug_{i}_{random_file}")
               
                shutil.copy(src, dst)
                total_augmented += 1
               
    print(f"\n HOÀN TẤT! Đã tạo thêm tổng cộng {total_augmented} ảnh mới.")
    print(" LƯU Ý: Không chạy file này lần 2 để tránh bị trùng lặp dữ liệu!")


# --- PHẦN CHẠY CHÍNH ---
if __name__ == "__main__":
    # dataset_final được tạo ra từ file split_data.py
    path_to_train = "dataset/train"
   
    balance_train_data(path_to_train)