import db
import json
from decimal import Decimal

def get_users():
    # Establish database connection
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            query_users = """
            SELECT 
                u.id,
                u.name,
                u.surname,
                u.job_position,
                u.is_patient,
                u.is_osm,
                u.is_specialist,
                u.is_admin,
                u.email,
                u.province,
                sr.N
            FROM 
                (
                    SELECT 
                        sender_id,
                        COUNT(*) as N 
                    FROM 
                        submission_record 
                    GROUP BY 
                        sender_id
                ) sr
            JOIN 
                (
                    SELECT * 
                    FROM user 
                    WHERE is_patient = 0
                    OR is_osm = 1
                    OR is_specialist = 1
                    OR is_admin = 1
                ) u
            ON 
                sr.sender_id = u.id;
            """
            cursor.execute(query_users)
            users_query = cursor.fetchall()
            print(users_query)
            # Format Output
            mapped_data = map_user_data(users_query)

            # Print the output in JSON-like format
            output = mapped_data
    except Exception as e:
        output = json.dumps({"error": f"An error occurred while fetching user accounts: {e}"})
        return output
    
    finally:
        # Close Connection
        connection.close()
    
    return output

def map_user_data(data):
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
        
        # Determine roles based on flags
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

