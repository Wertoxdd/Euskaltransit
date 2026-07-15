import urllib.request

url = "https://upload.wikimedia.org/wikipedia/commons/5/52/Bilbobuslogo.svg"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        svg_data = response.read().decode('utf-8')
        with open('static/img/logo_bilbobus_real.svg', 'w', encoding='utf-8') as f:
            f.write(svg_data)
        print("SVG descargado exitosamente.")
except Exception as e:
    print(f"Error: {e}")
