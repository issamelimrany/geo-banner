import os
import pandas as pd
from PIL import Image
from shapely.geometry import Point
import pytesseract
from ultralytics import YOLO
import json

# ----------------------------
# CONFIG
# ----------------------------
IMAGES_DIR = "streetview_business_poc"
OUTPUT_CSV = "banner_detections.csv"
OSM_POIS_FILE = "pois.json"  
DETECTION_CONF = 0.3  # YOLO confidence threshold

# ----------------------------
# Load YOLOv8 model (banner detection)
# ----------------------------
# we can train your own custom model for banners, or use a pre-trained object detector
model = YOLO("yolov8n.pt")

# ----------------------------
# Load POIs
# ----------------------------
with open(OSM_POIS_FILE, "r") as f:
    pois = json.load(f)

poi_points = []
for poi in pois:
    if "lat" in poi and "lon" in poi:
        poi_points.append({
            "name": poi.get("name", ""),
            "type": poi.get("type", ""),
            "lat": poi["lat"],
            "lon": poi["lon"],
            "point": Point(poi["lon"], poi["lat"])
        })

# ----------------------------
# Process images
# ----------------------------
results = []

for img_file in os.listdir(IMAGES_DIR):
    if not img_file.lower().endswith((".jpg", ".png")):
        continue

    img_path = os.path.join(IMAGES_DIR, img_file)
    img = Image.open(img_path)

    # Run YOLOv8 detection
    detections = model.predict(img_path, conf=DETECTION_CONF, verbose=False)
    for det in detections:
        if det.boxes is None or len(det.boxes) == 0:
            continue
        for box, conf, cls in zip(det.boxes.xyxy, det.boxes.conf, det.boxes.cls):
            x1, y1, x2, y2 = box.tolist()
            crop = img.crop((x1, y1, x2, y2))
            text = pytesseract.image_to_string(crop, lang="eng")  # OCR text

            # Associate with nearest POI (optional)
            # Here we can use the pano filename or metadata lat/lon if available
            # For demo, we skip geographic association

            results.append({
                "image": img_file,
                "bbox": [x1, y1, x2, y2],
                "confidence": float(conf),
                "ocr_text": text.strip(),
                "poi_name": "",  # fill if you have lat/lon metadata
            })

# ----------------------------
# Save results
# ----------------------------
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved {len(results)} banner detections to {OUTPUT_CSV}")
