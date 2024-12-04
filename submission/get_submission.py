from flask import json, jsonify
import db

def get_submission_by_role(role, user_id):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "failed to connect to the database."}), 500
    
    roles = {
        "admin": "SELECT * FROM submission_record",
        "patient": """SELECT * FROM submission_record WHERE patient_id = sender_id AND sender_id = %s""",
        "osm": """SELECT * FROM submission_record WHERE sender_id = %s""",
        "dentist": """SELECT * FROM submission_record WHERE sender_id = %s"""
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute((roles.get(role, roles['admin'])), ((user_id,) if role != 'admin' else ()))
            query_submission = cursor.fetchall()
            result = [dict(zip([column[0] for column in cursor.description], row)) for row in query_submission]
            
            return jsonify(result), 200
    except Exception as e:
        return json.dumps({"error": f"an error occurred while getting submission by role: {str(e)}"}), 500
    
    finally:
        connection.close()
