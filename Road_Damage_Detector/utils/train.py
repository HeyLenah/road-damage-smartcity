from ultralytics import YOLO

def train_model(data_yaml, model_size='n', epochs=5, batch=16):
    model = YOLO(f'yolov8{model_size}.pt')
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch,
        patience=2,
        project='yolov8_training'
    )
    return model, results

def load_trained_model(model_path= "yolov8m.pt"):
    print(f"📦 Loading trained model from: {model_path}")
    return YOLO(model_path)
