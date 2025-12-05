# file: data_loader.py
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


IMG_SIZE = 224
BATCH_SIZE = 32


def _find_dataset_root(candidate):
    candidate = os.path.abspath(candidate)
    # candidates to check (covers dataset/, dataset/dataset/ and project-root/dataset)
    checks = [
        candidate,
        os.path.join(candidate, "dataset"),
        os.path.join(os.path.dirname(__file__), "..", "dataset"),
        os.path.join(os.path.dirname(__file__), "..", "dataset", "dataset"),
    ]
    # normalize and dedupe
    checks = list(dict.fromkeys(os.path.abspath(p) for p in checks))
    for path in checks:
        if os.path.isdir(path) and all(os.path.isdir(os.path.join(path, sub)) for sub in ("train", "val", "test")):
            return path
    # try searching one level deeper under candidate
    if os.path.isdir(candidate):
        for sub in os.listdir(candidate):
            subp = os.path.join(candidate, sub)
            if os.path.isdir(subp) and all(os.path.isdir(os.path.join(subp, s)) for s in ("train", "val", "test")):
                return subp
    raise FileNotFoundError(f"No dataset root with 'train','val','test' found under: {candidate}\nChecked: {checks}")


def create_generators(dataset_dir="dataset"):
    dataset_root = _find_dataset_root(dataset_dir)

    # 1. Cấu hình Augmentation cho Train
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )


    # 2. Val và Test chỉ cần Preprocess, KHÔNG Augment
    test_val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)


    # 3. Load dữ liệu (dùng os.path.join)
    train_dir = os.path.join(dataset_root, "train")
    val_dir = os.path.join(dataset_root, "val")
    test_dir = os.path.join(dataset_root, "test")


    train_gen = train_datagen.flow_from_directory(
        directory=train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )


    val_gen = test_val_datagen.flow_from_directory(
        directory=val_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )


    test_gen = test_val_datagen.flow_from_directory(
        directory=test_dir,
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
    dataset_candidate = os.path.join(project_root, "dataset")
    try:
        train_gen, val_gen, test_gen = create_generators(dataset_candidate)
        print(f"\n✅ Load thành công!")
        print(f"- Số lớp bệnh (Class): {train_gen.num_classes}")
        print(f"- Số ảnh Train: {train_gen.samples}")
        print(f"- Số ảnh Val:   {val_gen.samples}")
        print(f"- Số ảnh Test:  {test_gen.samples}")
        print("\nDanh sách các lớp bệnh:", list(train_gen.class_indices.keys())[:10], "...")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")