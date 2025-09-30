import pandas as pd
from PIL import Image
import os
import random

# ----------------------------
# CONFIG
# ----------------------------
CSV_FILE = "banner_detections.csv"  
IMAGES_DIR = "streetview_business_poc"
SAMPLE_SIZE = 50                     # number of rows to sample

# ----------------------------
# Load CSV
# ----------------------------
df = pd.read_csv(CSV_FILE)
print(f"Total rows in CSV: {len(df)}\n")

# ----------------------------
# Sample rows
# ----------------------------
sample_rows = df.sample(min(SAMPLE_SIZE, len(df)))
print("Sample rows info:\n")
print(sample_rows[['image', 'confidence', 'ocr_text', 'poi_name']])

# ----------------------------
# Preview full images
# ----------------------------
for idx, row in sample_rows.iterrows():
    img_path = os.path.join(IMAGES_DIR, row['image'])
    if not os.path.exists(img_path):
        print(f"Image {row['image']} not found, skipping...")
        continue

    img = Image.open(img_path)

    print(f"\nShowing full image: {row['image']}, POI: {row['poi_name']}, OCR text: {row['ocr_text']}")
    img.show()
