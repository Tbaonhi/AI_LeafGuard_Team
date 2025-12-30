import os
import json
import numpy as np
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report, confusion_matrix


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


def train_model(model, train_gen, val_gen, epochs=20, class_weights=None):
    # Tạo thư mục models nếu chưa có
    if not os.path.exists("models"):
        os.makedirs("models")
   
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            "models/MobileNetV2_best.h5",
            save_best_only=True,
            monitor="val_accuracy",
            mode="max",
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            patience=5,
            restore_best_weights=True,
            monitor="val_loss",
            verbose=1
        )
    ]

    # Train với class weights nếu có
    fit_params = {
        "x": train_gen,
        "validation_data": val_gen,
        "epochs": epochs,
        "callbacks": callbacks
    }
    
    if class_weights:
        fit_params["class_weight"] = class_weights
        print(f"   [INFO] Đang sử dụng class weights để cân bằng dữ liệu")

    history = model.fit(**fit_params)

    return history


def evaluate_and_save_report(model, test_gen, class_names, output_dir="models"):
    print("\n" + "=" * 60)
    print("ĐANG ĐÁNH GIÁ MÔ HÌNH TRÊN TEST SET...")
    print("=" * 60)
    
    # Tạo thư mục nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Predict trên test set
    print("Đang dự đoán trên test set...")
    y_true = []
    y_pred = []
    
    # Reset generator
    test_gen.reset()
    steps = len(test_gen)
    
    for step in range(steps):
        batch_x, batch_y = next(test_gen)
        predictions = model.predict(batch_x, verbose=0)
        
        # Lấy true labels và predictions
        batch_y_true = np.argmax(batch_y, axis=1)
        batch_y_pred = np.argmax(predictions, axis=1)
        
        y_true.extend(batch_y_true)
        y_pred.extend(batch_y_pred)
        
        if (step + 1) % 10 == 0:
            print(f"  Đã xử lý {step + 1}/{steps} batches...")
    
    # Convert to numpy array
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Tính toán metrics
    print("\nĐang tính toán metrics...")
    report_dict = classification_report(
        y_true, y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    
    # Tính confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Lưu classification report
    report_file = os.path.join(output_dir, "evaluation_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Đã lưu evaluation report vào: {report_file}")
    
    # In tóm tắt
    print("\n📊 TÓM TẮT ĐÁNH GIÁ:")
    print(f"   - Accuracy: {report_dict['accuracy']:.4f}")
    print(f"   - Macro Avg F1: {report_dict['macro avg']['f1-score']:.4f}")
    print(f"   - Weighted Avg F1: {report_dict['weighted avg']['f1-score']:.4f}")
    
    # In top 5 classes tốt nhất và kém nhất
    class_f1 = {}
    for class_name in class_names:
        if class_name in report_dict:
            class_f1[class_name] = report_dict[class_name]['f1-score']
    
    sorted_classes = sorted(class_f1.items(), key=lambda x: x[1], reverse=True)
    
    print("\n🏆 TOP 5 CLASSES TỐT NHẤT:")
    for i, (class_name, f1) in enumerate(sorted_classes[:5], 1):
        print(f"   {i}. {class_name}: F1={f1:.4f}")
    
    print("\n⚠️  TOP 5 CLASSES KÉM NHẤT:")
    for i, (class_name, f1) in enumerate(sorted_classes[-5:], 1):
        print(f"   {i}. {class_name}: F1={f1:.4f}")
    
    return report_dict, cm