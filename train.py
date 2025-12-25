import os
# Tắt log rác của TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# Import code từ thư mục src của bạn
from src.data_loader import create_generators, get_class_weights_for_training
from src.model_trainer import build_mobilenetv2, train_model


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
   
    # Tính toán class weights để xử lý imbalanced data
    print("\nĐang tính toán class weights để cân bằng dữ liệu...")
    class_weights = get_class_weights_for_training(train_gen, dataset_path)
   
    # 2. Xây dựng Model
    print("\nĐang xây dựng MobileNetV2...")
    model = build_mobilenetv2(num_classes)
   
    # 3. Train Model với class weights
    print("\nBắt đầu Train (với class weights để xử lý imbalanced data)...")
    history = train_model(model, train_gen, val_gen, epochs=20, class_weights=class_weights)
   
    # 4. Lưu Model cuối cùng
    print("Đang lưu model kết quả...")
    model.save("models/plant_disease_final.h5")
    print("CHÚC MỪNG! Đã train xong. Model nằm trong thư mục 'models/'")