import os
from PIL import Image


def clean_data(root_path):
    valid_ext = {".jpg", ".jpeg", ".png", ".bmp"}
    removed_count = 0
   
    print(f"--- Bắt đầu kiểm tra thư mục: {root_path} ---")


    for folder, _, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(folder, file)
           
            # 1. Kiểm tra đuôi file
            ext = os.path.splitext(file)[1].lower()
            if ext not in valid_ext:
                os.remove(file_path)
                print(f"Xóa file sai định dạng: {file}")
                removed_count += 1
                continue


            # 2. Kiểm tra file hỏng (Corrupted)
            try:
                img = Image.open(file_path)
                img.verify() # Verify file integrity
                img.close()
                # Reload để check kỹ hơn (verify đôi khi bỏ sót)
                img = Image.open(file_path)
                img.transpose(Image.FLIP_LEFT_RIGHT)
                img.close()
            except (IOError, SyntaxError) as e:
                os.remove(file_path)
                print(f"Xóa ảnh hỏng: {file_path}")
                removed_count += 1


    print(f"--- Hoàn tất! Tổng số file đã xóa: {removed_count} ---")


if __name__ == "__main__":
    data_path = "data_raw/PlantVillage"
    if os.path.exists(data_path):
        clean_data(data_path)
    else:
        print(f"Lỗi: Không tìm thấy thư mục '{data_path}'")
        print("Hãy kiểm tra xem bạn đã giải nén đúng chỗ chưa!")