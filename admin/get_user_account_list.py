from admin.admin_mapper import map_user_list_data
import db
import json
from decimal import Decimal

def users_list():
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            user_list_query = fetch_user_list(cursor)
            user_list = map_user_list_data(user_list_query)

            output = user_list
    except Exception as e:
        return json.dumps({"error": f"An error occurred while fetching user accounts: {e}"}),500
    
    finally:
        connection.close()
    
    return output

def fetch_user_list(cursor):
    query ="""
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
    cursor.execute(query)
    user_list_query = cursor.fetchall()

    return user_list_query