# file: data_loader.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import os


IMG_SIZE = 224
BATCH_SIZE = 32


def create_generators(dataset_dir="dataset"):
    # 1. Cấu hình Augmentation cho Train
    # LƯU Ý: Dùng preprocess_input của MobileNetV2 thay vì rescale=1./255
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input, # Quan trọng: Đưa về [-1, 1]
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )


    # 2. Val và Test chỉ cần Preprocess, KHÔNG Augment
    test_val_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )


    # 3. Load dữ liệu
    train_gen = train_datagen.flow_from_directory(
        directory=f"{dataset_dir}/train",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )


    val_gen = test_val_datagen.flow_from_directory(
        directory=f"{dataset_dir}/val",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
   
    test_gen = test_val_datagen.flow_from_directory(
        directory=f"{dataset_dir}/test",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )


    return train_gen, val_gen, test_gen
# --- PHẦN KIỂM TRA DATA LOADER ---
if __name__ == "__main__":
    print("--- Đang kiểm tra Data Loader ---")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_path = os.path.join(project_root, "dataset")

    if not os.path.exists(dataset_path):
        print(f"Lỗi: Không thấy thư mục '{dataset_path}'. Bạn đã chạy split_data.py chưa? (see src/split_data.py)")
    else:
        try:
            # Gọi hàm để xem nó load được bao nhiêu ảnh
            train_gen, val_gen, test_gen = create_generators(dataset_path)
               
            print(f"\n✅ Load thành công!")
            print(f"- Số lớp bệnh (Class): {train_gen.num_classes}")
            print(f"- Số ảnh Train: {train_gen.samples}")
            print(f"- Số ảnh Val:   {val_gen.samples}")
            print(f"- Số ảnh Test:  {test_gen.samples}")
            print("\nDanh sách các lớp bệnh:", list(train_gen.class_indices.keys())[:5], "...")
               
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {e}")