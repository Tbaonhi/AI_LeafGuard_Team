### Trinh (member 1)
chạy lệnh terminal 
git checkout -b "setup_dataset"
# 1. download folder dataset 
# 2. push lên github

### Nhi (member 2)
chạy lệnh terminal 
git checkout -b "checkout_data"
git pull origin main
# 1. tạo file src/clean_data.py 
---
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
---
# 2. chạy file clean_data.py 
gõ lệnh vào terminal
py .\src\clean_data.py 

chạy lệnh terminal 
git checkout -b "split_dataset"

# 1. Tạo file src/split_data.py
---
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

    print(f"Đang chia dữ liệu từ '{root_dir}' sang '{output_dir}'...")

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
    print(f" Dữ liệu mới nằm tại: {output_dir}/")

if __name__ == "__main__":
    split_dataset()
---

# 2. chaỵ file split_data.py với lệnh
py .\src\split_data.py
# 3. Push code lên github

### Nhung
chạy lệnh terminal 
git checkout -b "balance_data"
git pull origin main

# 1. Tạo file balance_data.py

---
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
    print("LƯU Ý: Không chạy file này lần 2 để tránh bị trùng lặp dữ liệu!")

# --- PHẦN CHẠY CHÍNH ---
if __name__ == "__main__":
    path_to_train = "dataset/train"  
    balance_train_data(path_to_train)
---
# 2. run file 
py .\src\balance_data.py
# 3. push lên github

### Trâm ( Data Generators (Chuẩn hóa cho MobileNetV2) )
chạy lệnh terminal 
git checkout -b "data_generators"
git pull origin main

# 1. Tạo file /src/data_loader.py
---
# file: data_loader.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

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
    
import os
if not os.path.exists("dataset"):
    print("Lỗi: Không thấy thư mục 'dataset'. Bạn đã chạy split_data.py chưa?")
else:
    try:
        # Gọi hàm để xem nó load được bao nhiêu ảnh
        train_gen, val_gen, test_gen = create_generators("dataset")
            
        print(f"\n Load thành công!")
        print(f"- Số lớp bệnh (Class): {train_gen.num_classes}")
        print(f"- Số ảnh Train: {train_gen.samples}")
        print(f"- Số ảnh Val:   {val_gen.samples}")
        print(f"- Số ảnh Test:  {test_gen.samples}")
        print("\nDanh sách các lớp bệnh:", list(train_gen.class_indices.keys())[:5], "...")
            
    except Exception as e:
        print(f" Có lỗi xảy ra: {e}")
---
# 2. Chạy file này 
py .\src\data_loader.py
# 3. Push lên github

### Trinh 
git checkout -b "train_data"
git pull origin main

# 1.  Tạo file src/model_trainer.py
---
import os 
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

def build_mobilenetv2(num_classes):
    # (Giữ nguyên code của bạn ở đoạn này)
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.2)(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    
    model = Model(inputs=base_model.input, outputs=outputs)
    
    model.compile(
        optimizer=Adam(learning_rate=0.0005),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

def train_model(model, train_gen, val_gen, epochs=20):
    # --- SỬA Ở ĐÂY: Tạo thư mục models nếu chưa có ---
    if not os.path.exists("models"):
        os.makedirs("models")
    # ------------------------------------------------
    
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            "models/MobileNetV2_best.h5",
            save_best_only=True,
            monitor="val_accuracy",
            mode="max",
            verbose=1 # Thêm verbose để nhìn thấy khi nào nó lưu
        ),
        tf.keras.callbacks.EarlyStopping(
            patience=5,
            restore_best_weights=True,
            monitor="val_loss",
            verbose=1
        )
    ]

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks
    )

    return history
---
# 2. Tạo file train.py (ở thư mục root)
---
import os
# Tắt log rác của TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Import code từ thư mục src của bạn
from src.data_loader import create_generators  # Import file của Member 3 (Đã sửa)
from src.model_trainer import build_mobilenetv2, train_model # Import code của bạn

if __name__ == "__main__":
    print("--- BẮT ĐẦU CHƯƠNG TRÌNH HUẤN LUYỆN ---")

    # 1. Load Dữ Liệu
    # Đảm bảo bạn đã có folder 'dataset' (do Member 1 tạo ra)
    dataset_path = "dataset"
    
    if not os.path.exists(dataset_path):
        print(f"LỖI: Không tìm thấy thư mục '{dataset_path}'")
        exit()
        
    print(f"Đang load dữ liệu từ: {dataset_path}")
    train_gen, val_gen, test_gen = create_generators(dataset_path)
    
    # Lấy số lớp bệnh
    num_classes = train_gen.num_classes
    print(f"Đã tìm thấy {num_classes} loại bệnh/nhãn.")
    
    # 2. Xây dựng Model
    print("Đang xây dựng MobileNetV2...")
    model = build_mobilenetv2(num_classes)
    
    # 3. Train Model
    print("Bắt đầu Train (Code của bạn đang chạy!)...")
    history = train_model(model, train_gen, val_gen, epochs=20)
    
    # 4. Lưu Model cuối cùng
    print("Đang lưu model kết quả...")
    model.save("models/plant_disease_final.h5")
    print("CHÚC MỪNG! Đã train xong. Model nằm trong thư mục 'models/'")
---
# 3. run file train.py
# 4. Push lên github

