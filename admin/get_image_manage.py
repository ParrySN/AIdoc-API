import db
import json
import math
from decimal import Decimal
from admin.admin_mapper import map_image_manage_list_data


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
        return json.dumps({"error": f"An error occurred while fetching image records: {e}"}), 500
    finally:
        connection.close()

    return output


def fetch_image_manage_list(cursor, limit, offset, data):
    query = """
        SELECT 
            sr.id, sr.fname, sr.created_at, sr.ai_prediction, 
            u1.name AS user_name, u1.surname AS user_surname,
            sr.special_request, sr.location_province, 
            sr.dentist_id, sr.dentist_feedback_comment,
            u1.national_id, u2.name AS dentist_name, 
            u2.surname AS dentist_surname
        FROM submission_record sr
        LEFT JOIN user u1 ON sr.sender_id = u1.id
        LEFT JOIN user u2 ON sr.dentist_id = u2.id
        LEFT JOIN user u3 ON sr.patient_id = u3.id
    """

    conditions, params = build_conditions(data)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY sr.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def fetch_total_count(cursor, data):
    query = """
        SELECT COUNT(*) 
        FROM submission_record sr
        LEFT JOIN user u1 ON sr.sender_id = u1.id
        LEFT JOIN user u2 ON sr.dentist_id = u2.id
        LEFT JOIN user u3 ON sr.patient_id = u3.id
    """

    conditions, params = build_conditions(data)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, tuple(params))
    return cursor.fetchone()[0]


def build_conditions(data):
    conditions = []
    params = []

    # Search term
    if data.get('search_term'):
        search_pattern = set_input(data['search_term'])
        conditions.append(f""" 
            sr.fname LIKE %s OR
            sr.sender_phone LIKE %s OR
            sr.patient_national_id LIKE %s OR
            sr.dentist_feedback_comment LIKE %s OR
            sr.dentist_feedback_code LIKE %s OR
            sr.dentist_feedback_date LIKE %s OR
            sr.location_district LIKE %s OR
            sr.location_amphoe LIKE %s OR
            sr.location_province LIKE %s OR
            sr.location_zipcode LIKE %s OR
            u1.name LIKE %s OR
            u1.surname LIKE %s OR
            u1.national_id LIKE %s OR
            u1.email LIKE %s OR
            u1.phone LIKE %s OR
            u1.province LIKE %s OR
            u2.name LIKE %s OR
            u2.surname LIKE %s OR
            u2.national_id LIKE %s OR
            u2.email LIKE %s OR
            u2.phone LIKE %s OR
            u2.province LIKE %s OR
            u3.name LIKE %s OR
            u3.surname LIKE %s OR
            u3.national_id LIKE %s OR
            u3.email LIKE %s OR
            u3.phone LIKE %s OR
            u3.province LIKE %s
        """)
        params.extend([search_pattern] * 28)

    # Priority filter
    if data.get('priority'):
        priority = set_input(data['priority'])
        conditions.append("sr.special_request LIKE %s")
        params.append(priority)

    # Dentist check filter
    if data.get('dentist_checked') is not None:
        if data['dentist_checked'].lower() == 'true':
            conditions.append("sr.dentist_id IS NOT NULL")
        else:
            conditions.append("sr.dentist_id IS NULL")

    # Province filter
    if data.get('province'):
        province = set_input(data['province'])
        conditions.append("sr.location_province LIKE %s")
        params.append(province)

    # Dentist ID filter
    if data.get('dentist_id'):
        dentist_id = set_input(data['dentist_id'])
        conditions.append("sr.dentist_id LIKE %s")
        params.append(dentist_id)

    return conditions, params


def set_input(input):
    return f"%{input}%" if input else "%%"
