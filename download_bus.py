import urllib.request
import ssl
import zipfile
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.bilbao.eus/opendata/datos/bilbobus-gtfs"
zip_path = "datos_bus/bilbobus_gtfs.zip"

if not os.path.exists("datos_bus"):
    os.makedirs("datos_bus")

print("Descargando GTFS de Bilbobus...")
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx) as response:
    data = response.read()
    with open(zip_path, "wb") as f:
        f.write(data)
    print(f"Descargado: {len(data)} bytes")

print("Descomprimiendo...")
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall("datos_bus/")
    print("Archivos extraídos:", z.namelist())

print("Done!")
