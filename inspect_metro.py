import csv

print("=== ROUTES ===")
with open("datos_metro/routes.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"  {row['route_id']} | {row['route_short_name']} | {row.get('route_long_name','')} | type={row.get('route_type','')} | color={row.get('route_color','')}")

print("\n=== STOPS (first 40) ===")
with open("datos_metro/stops.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 40:
            break
        print(f"  {row['stop_id']} | {row['stop_name']} | {row['stop_lat']},{row['stop_lon']} | type={row.get('location_type','')}")

print("\n=== SHAPES (unique IDs) ===")
shape_ids = set()
with open("datos_metro/shapes.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        shape_ids.add(row["shape_id"])
for sid in sorted(shape_ids):
    print(f"  {sid}")

print("\n=== TRIPS (sample, first 10) ===")
with open("datos_metro/trips.txt", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 10:
            break
        print(f"  route={row['route_id']} | trip={row['trip_id']} | shape={row.get('shape_id','')} | headsign={row.get('trip_headsign','')}")
