from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import io
import base64
from PIL import Image
import numpy as np
from ultralytics import YOLO

app = FastAPI()

# Load the YOLO model
model = YOLO("best.pt")  # Ensure 'best.pt' is included in your deployment package

# Define response model
class PotholeDetectionResponse(BaseModel):
    pothole_detected: bool
    num_potholes: int
    image: str

@app.post("/predict", response_model=PotholeDetectionResponse)
async def predict(file: UploadFile = File(...)):
    # Read uploaded image file
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # Run YOLO prediction
    img_np = np.array(image)
    results = model.predict(img_np)

    # Count detections
    num_potholes = len(results[0].boxes)
    pothole_detected = num_potholes > 0

    # Draw detection boxes
    img_with_boxes = results[0].plot()  # numpy array
    img_with_boxes_pil = Image.fromarray(img_with_boxes)

    # Convert to base64
    buffered = io.BytesIO()
    img_with_boxes_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Return response
    return PotholeDetectionResponse(
        pothole_detected=pothole_detected,
        num_potholes=num_potholes,
        image=img_str
    )
