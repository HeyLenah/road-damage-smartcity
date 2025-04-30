from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import io
import base64
from PIL import Image
import numpy as np
from ultralytics import YOLO

app = FastAPI()

model = YOLO("best.pt")  # Make sure the path is correct

def detect_potholes(image: Image) -> (bool, np.ndarray):
    img_np = np.array(image)

    results = model.predict(img_np)

    img_with_boxes = results[0].plot()  # Draw the bounding boxes

    # Convert the image with boxes to PIL format
    img_with_boxes_pil = Image.fromarray(img_with_boxes)

    pothole_detected = len(results[0].boxes) > 0  # True if potholes are detected

    return pothole_detected, img_with_boxes_pil

# Response model
class PotholeDetectionResponse(BaseModel):
    pothole_detected: bool
    image: str

@app.post("/predict/", response_model=PotholeDetectionResponse)
async def predict(file: UploadFile = File(...)):
    # Read the image
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes))

    # Run detection
    pothole_detected, img_with_boxes = detect_potholes(image)

    # Convert the result image to base64
    buffered = io.BytesIO()
    img_with_boxes.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return PotholeDetectionResponse(
        pothole_detected=pothole_detected,
        image=img_str
    )
