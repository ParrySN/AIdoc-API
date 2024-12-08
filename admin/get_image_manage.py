from admin.admin_mapper import map_image_manage_list_data, map_user_list_data
import db
import json
from decimal import Decimal
import math

def image_manage_list(data):
    if data['limit'] <= 0 or data['page'] <= 0:
        return json.dumps({"error": "Invalid 'limit' or 'page' values."}), 400
    offset = (data['page'] - 1) * data['limit']

    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500

    try:
        with connection.cursor() as cursor:
            image_manage_list_query = fetch_image_manage_list(cursor, data['limit'], offset, data)
            image_manage_list = map_image_manage_list_data(image_manage_list_query)

            total_count = fetch_total_count(cursor, data)

            total_pages = math.ceil(total_count / data['limit'])

            output = {
                "data": image_manage_list,
                "pagination": {
                    "limit": data['limit'],
                    "page": data['page'],
                    "total_count": total_count,
                    "total_pages": total_pages
                }
            }

    except Exception as e:
        return json.dumps({"error": f"An error occurred while fetching user accounts: {e}"}), 500
    finally:
        connection.close()

    return output

def fetch_image_manage_list(cursor, limit, offset, data):
    query = """
        SELECT 
            sr.id,
            sr.fname,
            sr.created_at,
            sr.ai_prediction,
            u1.name AS user_name,
            u1.surname AS user_surname,
            sr.special_request,
            sr.location_province,
            sr.dentist_id,
            sr.dentist_feedback_comment,
            u1.national_id,
            u2.name AS dentist_name,
            u2.surname AS dentist_surname
        FROM submission_record sr
        LEFT JOIN user u1 
            ON sr.sender_id = u1.id
        LEFT JOIN user u2 
            ON sr.dentist_id = u2.id
        LEFT JOIN user u3
            ON sr.patient_id = u3.id
    """
    
    if data:
        query += """
            WHERE 
            sr.special_request LIKE %s
            OR sr.dentist_id is %s
            OR sr.location_province LIKE %s
            OR sr.dentist_id LIKE %s
            OR sr.fname LIKE %s
            OR sr.sender_phone LIKE %s
            OR sr.patient_national_id LIKE %s
            OR sr.dentist_feedback_comment LIKE %s
            OR sr.dentist_feedback_code LIKE %s
            OR sr.dentist_feedback_date LIKE %s
            OR sr.location_district LIKE %s
            OR sr.location_amphoe LIKE %s
            OR sr.location_province LIKE %s
            OR sr.location_zipcode LIKE %s
            OR u1.name LIKE %s
            OR u1.surname LIKE %s
            OR u1.national_id LIKE %s
            OR u1.email LIKE %s
            OR u1.phone LIKE %s
            OR u1.province LIKE %s
            OR u2.name LIKE %s
            OR u2.surname LIKE %s
            OR u2.national_id LIKE %s
            OR u2.email LIKE %s
            OR u2.phone LIKE %s
            OR u2.province LIKE %s
            OR u3.name LIKE %s
            OR u3.surname LIKE %s
            OR u3.national_id LIKE %s
            OR u3.email LIKE %s
            OR u3.phone LIKE %s
            OR u3.province LIKE %s
        """
        search_pattern = f"%{data['search_term']}%" if data['search_term'] else ""
        cursor.execute(query + " ORDER BY sr.created_at DESC LIMIT %s OFFSET %s", 
                       (data['priority'], data['dentist_checked'], data['province'], data['dentist_id'], 
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, limit, offset))
    else:
        query += " ORDER BY sr.created_at DESC LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))

    image_manage_list_query = cursor.fetchall()
    return image_manage_list_query

def fetch_total_count(cursor, data):
    query = """
        SELECT COUNT(*) 
        FROM submission_record sr
        LEFT JOIN user u1 ON sr.sender_id = u1.id
        LEFT JOIN user u2 ON sr.dentist_id = u2.id
        LEFT JOIN user u3 ON sr.patient_id = u3.id
    """

    if data:
        query += """
            WHERE 
            sr.special_request LIKE %s
            OR sr.dentist_id is %s
            OR sr.location_province LIKE %s
            OR sr.dentist_id LIKE %s
            OR sr.fname LIKE %s
            OR sr.sender_phone LIKE %s
            OR sr.patient_national_id LIKE %s
            OR sr.dentist_feedback_comment LIKE %s
            OR sr.dentist_feedback_code LIKE %s
            OR sr.dentist_feedback_date LIKE %s
            OR sr.location_district LIKE %s
            OR sr.location_amphoe LIKE %s
            OR sr.location_province LIKE %s
            OR sr.location_zipcode LIKE %s
            OR u1.name LIKE %s
            OR u1.surname LIKE %s
            OR u1.national_id LIKE %s
            OR u1.email LIKE %s
            OR u1.phone LIKE %s
            OR u1.province LIKE %s
            OR u2.name LIKE %s
            OR u2.surname LIKE %s
            OR u2.national_id LIKE %s
            OR u2.email LIKE %s
            OR u2.phone LIKE %s
            OR u2.province LIKE %s
            OR u3.name LIKE %s
            OR u3.surname LIKE %s
            OR u3.national_id LIKE %s
            OR u3.email LIKE %s
            OR u3.phone LIKE %s
            OR u3.province LIKE %s
        """
        search_pattern = f"%{data['search_term']}%" 
        cursor.execute(query, 
                       (data['priority'], data['dentist_checked'], data['province'], data['dentist_id'], 
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,
                        search_pattern, search_pattern, search_pattern,))
    else:
        cursor.execute(query)

    total_count = cursor.fetchone()[0]
    return total_count
