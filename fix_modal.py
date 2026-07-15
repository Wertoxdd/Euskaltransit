def update_index():
    path = 'app/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_html = """                            <div class="ruta-section">
                                <div class="ruta-header">
                                    <span style="background: #E3001B; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9em;">${ruta.linea}</span>
                                    <span style="font-weight: 600; font-size: 1.05em;">${destinoLimpio}</span>
                                </div>
                                <div class="grid-horas">
                                    ${ruta.horas_str.map(h => `<div class="hora-item">${h}</div>`).join('')}
                                </div>
                            </div>"""
                            
    new_html = """                            <div class="ruta-section" style="display: flex; gap: 16px; background: rgba(227,0,27,0.05); border: 1px solid rgba(227,0,27,0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px; align-items: stretch;">
                                <div class="ruta-header" style="display: flex; flex-direction: column; align-items: flex-start; gap: 6px; width: 130px; flex-shrink: 0; border-right: 1px solid rgba(255,255,255,0.1); padding-right: 12px;">
                                    <span style="background: #E3001B; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9em; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">${ruta.linea}</span>
                                    <span style="font-weight: 600; font-size: 0.85em; color: var(--text-secondary); line-height: 1.2;">${destinoLimpio}</span>
                                </div>
                                <div class="grid-horas" style="display: flex; flex-wrap: wrap; gap: 6px; flex: 1; align-content: flex-start;">
                                    ${ruta.horas_str.map(h => `<div class="hora-item" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.85em; color: #ddd; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'">${h}</div>`).join('')}
                                </div>
                            </div>"""
                            
    if old_html in content:
        content = content.replace(old_html, new_html)
        print("Updated HTML design in modal")
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_index()
