import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The exact string of the card-bus and bus-lines-container that was wrongly inserted
# It starts with \n<div class="linea-card" id="card-bus" ... and ends with </div>\n                    </div>
# Let's extract everything from <div class="linea-card" id="card-bus" up to the </div> of bus-lines-container

bus_block_match = re.search(r'(\n\s*<div class="linea-card" id="card-bus"[\s\S]*?<div id="bus-lines-container"[\s\S]*?</div>\n\s*</div>)', content)
if bus_block_match:
    bus_html = bus_block_match.group(1)
    
    # Remove it from its current location inside card-tranvia
    content = content.replace(bus_html, "")
    
    # We want to insert it after card-metro-l2
    # Find the end of card-metro-l2
    metro_l2_match = re.search(r'(<div class="linea-card" id="card-metro-l2"[\s\S]*?</div>\n\s*</div>)', content)
    
    if metro_l2_match:
        metro_l2_html = metro_l2_match.group(1)
        content = content.replace(metro_l2_html, metro_l2_html + "\n" + bus_html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arreglo de HTML aplicado.")
