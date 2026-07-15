import urllib.request
import ssl
import zipfile
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://cms.metrobilbao.eus/get/open_data/horarios/es"
zip_path = "datos_metro/metro_bilbao_gtfs.zip"

print("Descargando GTFS de Metro Bilbao...")
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx) as response:
    data = response.read()
    with open(zip_path, "wb") as f:
        f.write(data)
    print(f"Descargado: {len(data)} bytes")

print("Descomprimiendo...")
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall("datos_metro/")
    print("Archivos:", z.namelist())

print("Done!")
