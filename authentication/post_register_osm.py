import common.common_util as cu
import db
from flask import json

def post_osm(data):
    connection, cursor = db.get_db()
    try:
        with cursor:
            if check_national_id_and_phone_exists(cursor, data["national_id"],data["phone"]):
                return json.dumps({
                    "error": "Account with this National ID or phone already exists"
                }),

            valid_phone, message = cu.validate_phone(data["phone"])
            if not valid_phone:
                return json.dumps({
                        "error": message
                    }), 400
            
            valid_national_id, message = cu.validate_national_id(data["national_id"])
            if not valid_national_id:
                return json.dumps({
                        "error": message
                    }), 400
        
            confirm_national_id, message = cu.confirm_input(data["national_id"], data["confirm_national_id"], "รหัสบัตรประชาชน")
            if not confirm_national_id:
                return json.dumps({
                    "error": message
                }), 400

            confirm_phone, message = cu.confirm_input(data["phone"], data["confirm_phone"], "หมายเลขโทรศัพท์")
            if not confirm_phone:
                return json.dumps({
                    "error": message
                }), 400


            post_osm_query(cursor, data)
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

def check_national_id_and_phone_exists(cursor, national_id,phone):
    sql = "SELECT * FROM user WHERE national_id = %s OR phone = %s"
    cursor.execute(sql, (national_id,phone,))
    return cursor.fetchone() is not None

def post_osm_query(cursor, data):
    sql = """
        INSERT INTO user (
            name, surname, national_id, province,
            phone, job_position, hospital,is_osm, last_login
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    cursor.execute(sql, (
        data["name"],
        data["surname"],
        data["national_id"],
        data["province"],
        data["phone"],
        data["job_position"],
        data["hospital"],
        True
    ))