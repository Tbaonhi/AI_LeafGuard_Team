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


def train_model(model, train_gen, val_gen, epochs=20, class_weights=None):
    """
    Train model với class weights để xử lý imbalanced data
    
    Args:
        model: Model đã được compile
        train_gen: Train data generator
        val_gen: Validation data generator
        epochs: Số epochs để train
        class_weights: Dictionary chứa class weights {class_index: weight}
                       Nếu None, sẽ không sử dụng class weights
    """
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