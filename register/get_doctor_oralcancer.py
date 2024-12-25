import db
from flask import json

def get_data_oralcancer(id):
    connection, cursor = db.get_db2()
    try:
        doctor_data = fetch_data(cursor,id)
        output = {
            "message":"get successfully",
            "doctor_data": doctor_data
        }
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred","details":str(e)}),500
    finally:
        db.close_db()

    return output

def fetch_data(cursor,id):
    sql = """
        SELECT
            u.name,
            u.surname,
            u.email,
            u.phone,
            u.work,
            u.license,
            u.hospital,
            u.province,
            u.username,
        FROM
            users u
        """

    cursor.execute(sql,(id,))
    user_from_oralcancer = cursor.fetchall()
    return user_from_oralcancer