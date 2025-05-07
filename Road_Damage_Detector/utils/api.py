from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import io
import base64
from PIL import Image
import numpy as np
from ultralytics import YOLO

app = FastAPI()

model = YOLO("best.pt")  # Adjust this path to where your YOLO model is saved



def detect_potholes(image: Image) -> tuple[bool, np.ndarray]:
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
    image: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the homepage"}

@app.post("/predict", response_model=PotholeDetectionResponse)
async def predict(file: UploadFile = File(...)):
    # Read the image file
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes))

    # Run pothole detection and get the result image
    pothole_detected, img_with_boxes = detect_potholes(image)

    # Convert the image with bounding boxes to base64 string to return to the frontend
    buffered = io.BytesIO()
    img_with_boxes.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Return the response with the base64 image and detection result
    return PotholeDetectionResponse(
        pothole_detected=pothole_detected,
        image=img_str
    )
