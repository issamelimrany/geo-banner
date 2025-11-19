import os
import requests
import osmnx as ox
from shapely.geometry import Point
from PIL import Image
from io import BytesIO

# ----------------------------
# CONFIG
# ----------------------------
COMMUNE_NAME = "Antony, France"  
API_KEY = "your api key"      
OUT_DIR = "streetview_business_poc"
os.makedirs(OUT_DIR, exist_ok=True)

# ----------------------------
# 1. Fetch business POIs from OSM
# ----------------------------
# shop=* or amenity=*
tags = {"shop": True, "amenity": True}
gdf_pois = ox.features_from_place(COMMUNE_NAME, tags=tags)
print(f"Found {len(gdf_pois)} business POIs")

# ----------------------------
# 2. Street View metadata
# ----------------------------
META_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"
IMG_URL = "https://maps.googleapis.com/maps/api/streetview"

def streetview_metadata(lat, lon, radius=30):
    params = {"location": f"{lat},{lon}", "radius": radius, "key": API_KEY}
    r = requests.get(META_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def streetview_image(pano_id=None, lat=None, lon=None, heading=0,
                     fov=90, pitch=0, size="640x640"):
    params = {"size": size, "fov": fov, "pitch": pitch, "key": API_KEY}
    if pano_id:
        params["pano"] = pano_id
    else:
        params["location"] = f"{lat},{lon}"
        params["heading"] = heading
    r = requests.get(IMG_URL, params=params, timeout=20)
    if r.status_code == 200 and r.headers["Content-Type"].startswith("image"):
        return Image.open(BytesIO(r.content))
    return None

# ----------------------------
# 3. Process POIs
# ----------------------------
results = []
for idx, row in gdf_pois.iterrows():
    if row.geometry.geom_type != "Point":
        continue
    lat, lon = row.geometry.y, row.geometry.x
    md = streetview_metadata(lat, lon)
    if md.get("status") != "OK":
        continue
    pano_id = md.get("pano_id")
    date = md.get("date")
    # download one view facing north (0°) for demo
    img = streetview_image(pano_id=pano_id, heading=0)
    if img:
        out_path = os.path.join(OUT_DIR, f"{pano_id}.jpg")
        img.save(out_path)
        results.append({"lat": lat, "lon": lon, "pano_id": pano_id, "date": date})
        print("Saved pano:", pano_id, "date:", date)

print(f"\nFinished. Got {len(results)} valid panoramas.")
