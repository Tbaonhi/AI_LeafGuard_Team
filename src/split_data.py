# file: split_data.py
import os
import shutil
import random


# --- CẤU HÌNH ---
# Đảm bảo đường dẫn này đúng với máy của bạn
root_dir = "data_raw/PlantVillage"
output_dir = "dataset"


# Tỉ lệ chia
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
# Test sẽ là phần còn lại (0.15)


def split_dataset():
    # 1. Đặt hạt giống ngẫu nhiên (QUAN TRỌNG NHẤT)
    # Giúp kết quả chia giống hệt nhau ở mọi máy, mọi lần chạy
    random.seed(42)
   
    if not os.path.exists(root_dir):
        print(f"Lỗi: Không tìm thấy thư mục '{root_dir}'")
        return


    print(f"♻️  Đang chia dữ liệu từ '{root_dir}' sang '{output_dir}'...")


    # Tạo các thư mục đích
    train_dir = os.path.join(output_dir, "train")
    val_dir   = os.path.join(output_dir, "val")
    test_dir  = os.path.join(output_dir, "test")


    for path in [train_dir, val_dir, test_dir]:
        os.makedirs(path, exist_ok=True)


    # Lấy danh sách các lớp (thư mục con)
    classes = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
   
    total_files = 0


    for cls in classes:
        cls_path = os.path.join(root_dir, cls)
        images = os.listdir(cls_path)
       
        # Xáo trộn ngẫu nhiên danh sách ảnh
        random.shuffle(images)


        # Tính toán điểm cắt
        n = len(images)
        train_split = int(TRAIN_RATIO * n)
        val_split   = int((TRAIN_RATIO + VAL_RATIO) * n)


        # Tạo thư mục class bên trong train/val/test
        os.makedirs(os.path.join(train_dir, cls), exist_ok=True)
        os.makedirs(os.path.join(val_dir, cls), exist_ok=True)
        os.makedirs(os.path.join(test_dir, cls), exist_ok=True)


        print(f"   --> Đang xử lý lớp: {cls} ({n} ảnh)")


        for i, img in enumerate(images):
            src = os.path.join(cls_path, img)
           
            # Quyết định xem ảnh về đội nào
            if i < train_split:
                dst = os.path.join(train_dir, cls, img)
            elif i < val_split:
                dst = os.path.join(val_dir, cls, img)
            else:
                dst = os.path.join(test_dir, cls, img)
           
            shutil.copy(src, dst)
            total_files += 1


    print(f"\n HOÀN TẤT! Tổng cộng {total_files} ảnh đã được chia.")
    print(f"Dữ liệu mới nằm tại: {output_dir}/")


if __name__ == "__main__":
    split_dataset()