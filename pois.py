import os
import json
import osmnx as ox
from shapely.geometry import Point

COMMUNE_NAME = "Antony, France"  
OUT_JSON = "pois.json"

# ----------------------------
# 1. Fetch business POIs from OSM
# ----------------------------
tags = {"shop": True, "amenity": True, "office": True, "craft": True, "tourism": True}
gdf_pois = ox.features_from_place(COMMUNE_NAME, tags=tags)
print(f"Found {len(gdf_pois)} POIs")

# ----------------------------
# 2. Convert to list of dicts
# ----------------------------
pois_list = []
for idx, row in gdf_pois.iterrows():
    geom = row.geometry
    if geom is None:
        continue
    # handle both points and polygons
    if geom.geom_type == "Point":
        lat, lon = geom.y, geom.x
    elif geom.geom_type in ["Polygon", "MultiPolygon"]:
        lat, lon = geom.centroid.y, geom.centroid.x
    else:
        continue

    pois_list.append({
        "name": row.get("name", ""),
        "type": row.get("shop") or row.get("amenity") or row.get("office") or row.get("craft") or row.get("tourism") or "",
        "lat": lat,
        "lon": lon
    })

# ----------------------------
# 3. Save to JSON
# ----------------------------
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(pois_list, f, ensure_ascii=False, indent=2)

print(f"Saved {len(pois_list)} POIs to {OUT_JSON}")
