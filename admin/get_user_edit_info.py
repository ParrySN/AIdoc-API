
from flask import json, jsonify
import db

def user_info(id):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            user_info_query = fetch_user_info(cursor,id)

            if not user_info_query:
                return json.dumps({"error": "User not found."}), 400

            user_data = {
                "id": user_info_query[0],
                "name": user_info_query[1],
                "surname": user_info_query[2],
                "job_position": user_info_query[3],
                "is_patient": user_info_query[4],
                "is_osm": user_info_query[5],
                "is_specialist": user_info_query[6],
                "is_admin": user_info_query[7],
                "email": user_info_query[8],
                "province": user_info_query[9],
                "national_id": user_info_query[10],
                "hospital": user_info_query[11],
                "phone": user_info_query[12]
            }

    except Exception as e:
        return  json.dumps({"error": f"An error occurred while fetching user data: {e}"}), 500
    
    finally:
        connection.close()

    return jsonify(user_data)

def fetch_user_info(cursor,id):
    print(id)
    query ="""
        SELECT
            id,
            name,
            surname,
            job_position,
            is_patient,
            is_osm,
            is_specialist,
            is_admin,
            email,
            province,
            national_id,
            hospital,
            phone 
            FROM user 
        WHERE id = %s
            """
    cursor.execute(query,(id,))
    user_info_query = cursor.fetchone()

    return user_info_query