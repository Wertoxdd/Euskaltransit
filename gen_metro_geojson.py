import csv
import json

# Read shapes for the two longest routes (one per line direction)
# L1: ETX_PLE (Etxebarri -> Plentzia) 
# L2: BSR_KAB (Basauri -> Kabiezes)
TARGET_SHAPES = {
    "ETX_PLE": "L1 - Etxebarri / Plentzia",
    "BSR_KAB": "L2 - Basauri / Kabiezes",
}

shapes = {}
with open("datos_metro/shapes.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sid = row["shape_id"]
        if sid in TARGET_SHAPES:
            if sid not in shapes:
                shapes[sid] = []
            shapes[sid].append({
                "seq": int(row["shape_pt_sequence"]),
                "lon": float(row["shape_pt_lon"]),
                "lat": float(row["shape_pt_lat"]),
            })

features = []
for sid, name in TARGET_SHAPES.items():
    pts = sorted(shapes[sid], key=lambda x: x["seq"])
    coords = [[p["lon"], p["lat"]] for p in pts]
    
    # Asignar color real según la línea
    color = "#E3001B" if "L1" in name else "#888888"
    
    features.append({
        "type": "Feature",
        "properties": {
            "name": name,
            "shape_id": sid,
            "color": color,
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coords,
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features,
}

with open("static/metrobilbao.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False)

print(f"Generated metrobilbao.geojson with {len(features)} features")
for feat in features:
    print(f"  {feat['properties']['name']}: {len(feat['geometry']['coordinates'])} points")
