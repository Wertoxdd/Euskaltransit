def update_index():
    path = 'app/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the container stretching
    target_1 = 'display: flex; justify-content: space-between; align-items: stretch; margin-bottom: 20px; gap: 10px;'
    replace_1 = 'display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; gap: 10px;'
    
    # Fix the buttons container stretching
    target_2 = 'display: flex; gap: 6px; align-items: stretch; flex-shrink: 0;'
    replace_2 = 'display: flex; gap: 6px; align-items: center; flex-shrink: 0;'
    
    if target_1 in content:
        content = content.replace(target_1, replace_1)
        print("Replaced target_1")
    if target_2 in content:
        content = content.replace(target_2, replace_2)
        print("Replaced target_2")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_index()
