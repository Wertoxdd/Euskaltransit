import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.bilbao.eus/opendata/datos/bilbobus-gtfs"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as response:
        print("Status:", response.status)
        print("Content-Type:", response.headers.get('Content-Type'))
        print("Length:", response.headers.get('Content-Length'))
except Exception as e:
    print("Error:", e)
