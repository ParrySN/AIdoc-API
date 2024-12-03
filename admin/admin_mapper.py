def map_user_list_data(data):
    user_list = []
    
    for row in data:
        user = {
            "id": row[0],
            "name": row[1],
            "surname": row[2],
            "email": row[8] if row[8] else "None",
            "province": row[9],
            "job_position": row[3],
            "role": [],
            "total_submit": row[10]
        }
        
        if row[4] == 1:
            user["role"].append("patient")
        if row[5] == 1:
            user["role"].append("osm")
        if row[6] == 1:
            user["role"].append("specialist")
        if row[7] == 1:
            user["role"].append("admin")
        
        user_list.append(user)
    
    return user_list