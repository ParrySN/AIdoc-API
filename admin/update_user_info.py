
from flask import json, jsonify
import db

def updateUserInfo(data):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """
            UPDATE user
            SET 
                name = %s,
                surname = %s,
                job_position = %s,
                is_patient = %s,
                is_osm = %s,
                is_specialist = %s,
                is_admin = %s,
                email = %s,
                province = %s,
                national_id = %s,
                hospital = %s,
                phone = %s
                WHERE id = %s;
            """
            cursor.execute(sql, (
                data['name'], 
                data['surname'], 
                data['job_position'], 
                data['is_patient'], 
                data['is_osm'], 
                data['is_specialist'], 
                data['is_admin'], 
                data['email'], 
                data['province'], 
                data['national_id'], 
                data['hospital'], 
                data['phone'], 
                data['id'],
            ))
            connection.commit()
            output = {
                "message": "User information updated successfully.",
                "updated_info": data  # Returning the updated information for confirmation
            }
    except Exception as e:
        output = json.dumps({"error": f"An error occurred while fetching user data: {e}"})
        return output, 500
    
    finally:
        connection.close()

    return jsonify(output), 200