import csv

# Get all unique stop sequences per shape to understand line structure
shapes_stops = {}

with open("datos_metro/trips.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    trip_to_shape = {}
    for row in reader:
        trip_to_shape[row["trip_id"]] = row["shape_id"]

# Read stop_times to get the order of stops per trip
trip_stops = {}
with open("datos_metro/stop_times.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        tid = row["trip_id"]
        if tid not in trip_stops:
            trip_stops[tid] = []
        trip_stops[tid].append((int(row["stop_sequence"]), row["stop_id"]))

# Read stop names
stop_names = {}
with open("datos_metro/stops.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stop_names[row["stop_id"]] = row["stop_name"]

# For each shape, get one trip and its ordered stops
seen_shapes = set()
for tid, shape_id in sorted(trip_to_shape.items()):
    if shape_id in seen_shapes:
        continue
    seen_shapes.add(shape_id)
    if tid in trip_stops:
        stops = sorted(trip_stops[tid], key=lambda x: x[0])
        stop_list = [stop_names.get(s[1], s[1]) for s in stops]
        print(f"\nShape: {shape_id}")
        print(f"  Stops ({len(stops)}): {' -> '.join(stop_list)}")

# Also count shape points
print("\n=== SHAPE POINT COUNTS ===")
shape_counts = {}
with open("datos_metro/shapes.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sid = row["shape_id"]
        shape_counts[sid] = shape_counts.get(sid, 0) + 1
for sid, count in sorted(shape_counts.items()):
    print(f"  {sid}: {count} points")
