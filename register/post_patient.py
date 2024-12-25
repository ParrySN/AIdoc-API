import db
from flask import json
from . import get_patient_oralcancer

def post_patient(data):
    connection, cursor = db.get_db()
    try:
        if check_national_id_exists(cursor, data["national_id"]):
            return json.dumps({
                "error": "Patient with this National ID already exists"
            }), 400
        data["default_location"] = {
            'province': data.get("province", ""),
            'district': data.get("district", ""),
            'subdistrict': data.get("subdistrict", ""),
            'zipcode': data.get("zipcode", ""),
        }
        post_table_user(cursor, data)
        output = {
            "message": "Post successfully",
            "patient_data": data
        }

    except Exception as e:
        return json.dumps({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

    return output


def check_national_id_exists(cursor, national_id):
    sql = "SELECT 1 FROM user WHERE national_id = %s"
    cursor.execute(sql, (national_id,))
    return cursor.fetchone() is not None

def post_table_user(cursor, data):
    sql = """
        INSERT INTO user (
            name, surname, national_id, birthdate, sex, province,
            default_location, address, phone, job_position, is_patient
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    default_location_json = json.dumps(data["default_location"])
    cursor.execute(sql, (
        data["name"],
        data["surname"],
        data["national_id"],
        data["birthdate"],
        data["sex"],
        data["province"],
        default_location_json,
        data["address"],
        data["phone"],
        data["job_position"],
        True
    ))