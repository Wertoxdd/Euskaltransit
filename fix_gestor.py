def update_gestor():
    path = 'app/gestor.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Let's relax the calendar date range check so we only care about the day of the week,
    # because the GTFS dataset dates might be expired, causing missing lines.
    
    target_logic = """        # Evaluate standard calendar
        for srv_id, c in self.calendar_bus.items():
            if c["start_date"] <= today_str <= c["end_date"]:
                if c[current_day_name] == "1":
                    active_services.add(srv_id)"""
                    
    relaxed_logic = """        # Evaluate standard calendar (Relaxed date check to show all lines)
        for srv_id, c in self.calendar_bus.items():
            if c[current_day_name] == "1":
                active_services.add(srv_id)"""
                
    if target_logic in content:
        content = content.replace(target_logic, relaxed_logic)
        print("Backend relaxed logic applied")
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_gestor()
