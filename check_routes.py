import csv

with open('datos/routes.txt', mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rid = row["route_id"]
        short = row["route_short_name"]
        long_name = row.get("route_long_name", "")
        rtype = row.get("route_type", "")
        color = row.get("route_color", "")
        print(f"{rid} | {short} | {long_name} | type={rtype} | color={color}")
