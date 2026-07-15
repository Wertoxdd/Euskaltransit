import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Lógica GTFS
old_gtfs = """        function limpiarDestinoGTFS(destinoRaw) {
            if (!destinoRaw) return 'Dirección Desconocida';
            let dest = destinoRaw;
            // Eliminar códigos y quedarse con lo último tras la barra "/"
            if (dest.includes('/')) {
                dest = dest.split('/').pop();
            }
            // Eliminar textos entre paréntesis tipo (SA) o (PT)
            dest = dest.replace(/\\(.*\\)/g, '');
            // Eliminar prefijos de línea si aún quedan (ej: "01 - San Inazio")
            dest = dest.replace(/^\\d{2}\\s*-\\s*/, '');
            return dest.trim();
        }"""
        
# If old python regex was used, it might be slightly different. Let's use regex to find the function.
gtfs_regex = r"function limpiarDestinoGTFS\(destinoRaw\) \{[\s\S]*?return dest\.trim\(\);\n\s*\}"
new_gtfs = """function limpiarDestinoGTFS(destinoRaw) {
            if (!destinoRaw) return 'Dirección Desconocida';
            let dest = destinoRaw.replace(/\\(.*?\\)/g, '').trim();
            if (dest.includes('/')) {
                let parts = dest.split('/');
                dest = parts[parts.length - 1].trim();
                if (!dest && parts.length > 1) dest = parts[parts.length - 2].trim();
            }
            dest = dest.replace(/^.*?-\\s*/, '');
            if (!dest) dest = destinoRaw.substring(0, 15) + '...';
            return dest.trim();
        }"""
content = re.sub(gtfs_regex, new_gtfs, content)

# 2. Accesibilidad (Color y Padding)
content = content.replace("--text-secondary: #a4b0be;", "--text-secondary: #d1d8e0;")

# Botón Activar Todas (Outline)
old_activar = "background: #E3001B; color: white; border: none;"
new_activar = "background: transparent; color: #E3001B; border: 1px solid #E3001B;"
content = content.replace(old_activar, new_activar)

# Botones de líneas (44x44px padding/touch target)
old_btn_style = "'padding: 4px 2px; border-radius: 4px; background: #333; color: #aaa; border: none; cursor: pointer; font-size: 10px; font-weight: bold; transition: all 0.2s;'"
new_btn_style = "'min-width: 44px; min-height: 44px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 6px; background: #333; color: #aaa; border: none; cursor: pointer; font-size: 11px; font-weight: bold; transition: all 0.2s;'"
content = content.replace(old_btn_style, new_btn_style)

# Grid layout for buttons (from 36px to 44px)
old_grid = "grid-template-columns: repeat(auto-fill, minmax(36px, 1fr));"
new_grid = "grid-template-columns: repeat(auto-fill, minmax(44px, 1fr));"
content = content.replace(old_grid, new_grid)


# 3. Jerarquía Visual (Líneas mapa opacity/weight)
# Bus
content = content.replace("weight: 4, opacity: 0.2", "weight: 4, opacity: 0.1")
content = content.replace("weight: 2, opacity: 0.9", "weight: 2, opacity: 0.5")
# Tranvia
content = content.replace("weight: 10, opacity: 0.15", "weight: 6, opacity: 0.08")
content = content.replace("weight: 4, opacity: 0.9", "weight: 2, opacity: 0.5")


# 4. Controles del Mapa
old_map = "zoomControl: false // Quitamos el control de zoom por defecto para reubicarlo\n        });"
new_map = """zoomControl: false
        });

        // Controles de Mapa Nativos
        L.control.zoom({ position: 'bottomright' }).addTo(map);
        
        const GeolocateControl = L.Control.extend({
            options: { position: 'bottomright' },
            onAdd: function() {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                const button = L.DomUtil.create('a', 'leaflet-control-geolocate', container);
                button.innerHTML = '🎯';
                button.href = '#';
                button.title = 'Ir a mi ubicación';
                button.style.fontSize = '18px';
                button.style.lineHeight = '30px';
                button.style.textAlign = 'center';
                
                L.DomEvent.on(button, 'click', function(e) {
                    L.DomEvent.preventDefault(e);
                    map.locate({setView: true, maxZoom: 16});
                });
                return container;
            }
        });
        map.addControl(new GeolocateControl());"""
content = content.replace(old_map, new_map)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Actualizaciones UI/UX y GTFS completadas.")
