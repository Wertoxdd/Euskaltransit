import csv
import json
import os

ruta_bus = "datos_bus"

routes = {}
with open(os.path.join(ruta_bus, "routes.txt"), "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        routes[row["route_id"]] = {
            "name": row.get("route_short_name", "BUS"),
            "color": f"#{row.get('route_color', '')}" if row.get('route_color') else "#E3001B"
        }

# Get one shape_id per (route_id, direction_id)
selected_shapes = {} # shape_id -> route_id
route_dirs_seen = set()

with open(os.path.join(ruta_bus, "trips.txt"), "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        r_id = row["route_id"]
        d_id = row.get("direction_id", "0")
        s_id = row.get("shape_id")
        
        if not s_id: continue
        
        key = (r_id, d_id)
        if key not in route_dirs_seen:
            route_dirs_seen.add(key)
            selected_shapes[s_id] = r_id

# Parse shapes
shapes_data = {} # shape_id -> list of (lat, lon, seq)
with open(os.path.join(ruta_bus, "shapes.txt"), "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        s_id = row["shape_id"]
        if s_id in selected_shapes:
            if s_id not in shapes_data:
                shapes_data[s_id] = []
            lat = float(row["shape_pt_lat"])
            lon = float(row["shape_pt_lon"])
            seq = int(row["shape_pt_sequence"])
            shapes_data[s_id].append((seq, lat, lon))

# Build GeoJSON
features = []
for s_id, pts in shapes_data.items():
    pts.sort(key=lambda x: x[0]) # sort by sequence
    coords = [[lon, lat] for seq, lat, lon in pts] # GeoJSON is [lon, lat]
    r_id = selected_shapes[s_id]
    r_info = routes[r_id]
    
    feature = {
        "type": "Feature",
        "properties": {
            "name": r_info["name"],
            "color": r_info["color"]
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coords
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

os.makedirs("static", exist_ok=True)
with open("static/bilbobus.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f)

print(f"Generated bilbobus.geojson with {len(features)} routes.")
