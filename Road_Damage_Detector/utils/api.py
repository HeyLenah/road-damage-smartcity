from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import io
import base64
from PIL import Image
import numpy as np
from ultralytics import YOLO

app = FastAPI()

model = YOLO("best.pt")  # Adjust this path to where your YOLO model is saved



def detect_potholes(image: Image) -> (bool, np.ndarray):
    img_np = np.array(image)

    results = model.predict(img_np)

    img_with_boxes = results[0].plot()  # This will automatically draw the boxes on the image

    # Convert the image with boxes to a PIL Image
    img_with_boxes_pil = Image.fromarray(img_with_boxes)

    # Detect if potholes are present based on the number of detected objects
    pothole_detected = len(results[0].boxes) > 0  # True if potholes are detected

    return pothole_detected, img_with_boxes_pil

# Response model
class PotholeDetectionResponse(BaseModel):
    pothole_detected: bool
    num_potholes: int
    image: str

@app.post("/predict", response_model=PotholeDetectionResponse)
async def predict(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes))

    pothole_detected, img_with_boxes = detect_potholes(image)
    num_potholes = len(model.predict(np.array(image))[0].boxes)

    buffered = io.BytesIO()
    img_with_boxes.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return PotholeDetectionResponse(
        pothole_detected=pothole_detected,
        num_potholes=num_potholes,
        image=img_str
    )
