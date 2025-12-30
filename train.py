import os
import tensorflow as tf
# Tắt log rác của TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# Import code từ thư mục src của bạn
from src.data_loader import create_generators, get_class_weights_for_training
from src.model_trainer import build_mobilenetv2, train_model, evaluate_and_save_report


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
   
    # 4. Load best model (đã được lưu bởi ModelCheckpoint)
    print("\nĐang load model tốt nhất...")
    best_model = tf.keras.models.load_model("models/MobileNetV2_best.h5")
    
    # 5. Đánh giá model trên test set và lưu report
    class_names = list(train_gen.class_indices.keys())
    evaluate_and_save_report(best_model, test_gen, class_names)
    
    # 6. Lưu Model cuối cùng (optional)
    print("\nĐang lưu model cuối cùng...")
    best_model.save("models/plant_disease_final.h5")
    
    print("\n" + "=" * 60)
    print("CHÚC MỪNG! Đã train xong.")
    print("=" * 60)
    print("📁 Các file đã được lưu:")
    print("   - models/MobileNetV2_best.h5 (Model tốt nhất)")
    print("   - models/plant_disease_final.h5 (Model cuối cùng)")
    print("   - models/evaluation_report.json (Báo cáo đánh giá)")