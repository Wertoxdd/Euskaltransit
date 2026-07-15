def update_index():
    path = 'app/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix default zoom levels
    content = content.replace("function abrirPanelMetro(estacion, marker, zoomNivel = 16)", "function abrirPanelMetro(estacion, marker, zoomNivel = 18)")
    content = content.replace("function abrirPanelBus(estacion, marker, zoomNivel = 17)", "function abrirPanelBus(estacion, marker, zoomNivel = 18)")
    
    # 2. Fix flyTo durations to make them snappier (0.8 -> 0.4, 0.5 -> 0.3)
    content = content.replace("duration: 0.8, easeLinearity: 0.4", "duration: 0.4, easeLinearity: 0.4")
    content = content.replace("duration: 0.5", "duration: 0.3")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_index()
