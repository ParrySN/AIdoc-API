from flask import jsonify
from db import connect_to_mysql
import pymysql

def get_patient_records(key):
    """Fetch user details from the aidoc_development database."""
    connection = connect_to_mysql()
    try:
        with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT 
                    sr.patient_id, 
                    sr.sender_id, 
                    sr.created_at, 
                    sr.biopsy_fname, 
                    sr.biopsy_comment, 
                    sr.id AS submission_id, 
                    sr.ai_prediction,
                    sr.dentist_feedback_code,
                    sr.dentist_feedback_comment,
                    sr.dentist_feedback_lesion,
                    sr.dentist_feedback_location,
                    sr.dentist_feedback_date,
                    sr.channel,
                    u.id AS user_id,
                    u.name AS user_name
                FROM 
                    submission_record sr
                JOIN 
                    user u ON sr.patient_id = u.id
                WHERE 
                    sr.patient_id = %s and sr.patient_id = u.id 
            """
            # Execute the query with the provided key
            cursor.execute(query, (key,))
            user = cursor.fetchall()

            if not user:
                return jsonify({"message": "No records found"}), 404
                
            return jsonify(user), 200
                

            
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()