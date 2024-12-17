
from flask import json, jsonify
import db

def getUserEditProfile(id):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT 
            id,
            name,
            surname,
            job_position,
            is_patient,
            is_osm,
            is_specialist,
            is_admin,email,
            province,
            national_id,
            hospital,
            phone 
            FROM user 
            WHERE id = %s"""
            cursor.execute(sql, (id,))
            user = cursor.fetchone()

            if not user:
                return json.dumps({"error": "User not found."}), 404

            user_data = {
                "id": user[0],
                "name": user[1],
                "surname": user[2],
                "job_position": user[3],
                "is_patient": user[4],
                "is_osm": user[5],
                "is_specialist": user[6],
                "is_admin": user[7],
                "email": user[8],
                "province": user[9],
                "national_id": user[10],
                "hospital": user[11],
                "phone": user[12]
            }

    except Exception as e:
        output = json.dumps({"error": f"An error occurred while fetching user data: {e}"})
        return output, 500
    
    finally:
        connection.close()

    return jsonify(user_data)