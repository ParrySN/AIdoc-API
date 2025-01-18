import common.common_util as cu
import db
from flask import json

def post_patient(data):
    connection, cursor = db.get_db()
    try:
        with cursor:
            if check_national_id_exists(cursor, data["national_id"]):
                return json.dumps({
                    "error": "Account with this National ID already exists"
                }), 409

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
                
            post_patient_query(cursor, data)
            connection.commit()
            update_submission_record(cursor, data)
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
    sql = "SELECT * FROM user WHERE national_id = %s"
    cursor.execute(sql, (national_id,))
    return cursor.fetchone() is not None

def post_patient_query(cursor, data):
    sql = """
        INSERT INTO user (
            name, surname, national_id, birthdate, sex, province,
            default_location, address, phone, job_position, is_patient, last_login
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    default_location = json.dumps({
    "province": data["province"],
    "district": data["district"],
    "amphoe": data["subdistrict"],
    "zipcode": data["zipcode"]
    })  
    cursor.execute(sql, (
        data["name"],
        data["surname"],
        data["national_id"],
        data["birthdate"],
        data["sex"],
        data["province"],
        default_location,
        data["address"],
        data["phone"],
        data["job_position"],
        True
    ))

def update_submission_record(cursor, data):
    print(data["national_id"])
    sql_get_id = "SELECT id FROM user WHERE national_id = %s"
    cursor.execute(sql_get_id, (data["national_id"],))
    patient_id = cursor.fetchone()["id"]
    print(patient_id)
    sql = """
        UPDATE submission_record
        SET patient_id = %s
        WHERE patient_national_id = %s;
    """
    cursor.execute(sql, (patient_id,data["national_id"],))