from admin.admin_mapper import map_image_manage_list_data, map_user_list_data
import db
import json
from decimal import Decimal

def image_manage_list():
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            image_manage_list_query = fetch_image_manage_list(cursor)
            image_manage_list = map_image_manage_list_data(image_manage_list_query)

            output = image_manage_list
    except Exception as e:
        return json.dumps({"error": f"An error occurred while fetching user accounts: {e}"}),500
    
    finally:
        connection.close()
    
    return output

def fetch_image_manage_list(cursor):
    query ="""
        SELECT 
            sr.id,
            sr.fname,
            sr.created_at,
            sr.ai_prediction,
            u.name AS user_name,
            u.surname AS user_surname,
            sr.special_request,
            sr.location_province,
            sr.dentist_id,
            sr.dentist_feedback_comment,
            u.national_id,
            u2.name AS dentist_name,
            u2.surname AS dentist_surname
        FROM submission_record sr
        LEFT JOIN user u 
            ON sr.sender_id = u.id
        LEFT JOIN user u2 
            ON sr.dentist_id = u2.id
        ORDER BY sr.created_at DESC
    """
    cursor.execute(query)
    image_manage_list_query = cursor.fetchall()

    return image_manage_list_query