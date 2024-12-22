import db
from flask import json
from . import get_patient_oralcancer

def post_patient(data):
    try:
        # Connect to the first database
        connection, cursor = db.get_db2()
        oralcancer_patient = get_patient_oralcancer.get_data_oralcancer(data["national_id"])
        db.close_db()
        connection, cursor = db.get_db()
        # Check for patient information
        if not oralcancer_patient["patient_info"]:
            post_table_user(cursor,data)
            message = "successfully register"
            output = {
            "message": message,
            "patient_info": data
            }
        else:
            patient_info = oralcancer_patient["patient_info"]
            first_name, last_name = patient_info[0]["fullname"].split(maxsplit=1)

            renamed_fields_info = {
                "name": first_name,
                "surname": last_name,
                "national_id": patient_info[0]["license"],
                "birthdate": patient_info[0]["birth_date"],
                "sex": patient_info[0]["sex"],
                "province": patient_info[0]["province"],
                "default_location": "none",
                "address": patient_info[0]["address"],
                "phone": patient_info[0]["phone"],
                "job_position": patient_info[0]["work"],
            }
            post_table_user(cursor,renamed_fields_info)
            message = "Adding old user to new database successfully"
            output = {
            "message": message,
            "patient_info": renamed_fields_info
            }
            
        db.close_db()
    except Exception as e:
        return json.dumps({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

    return json.dumps(output, ensure_ascii=False), 200


def post_table_user(cursor, data):
    sql = """
        INSERT INTO user (
            name, surname, national_id, birthdate, sex, province,
            default_location, address, phone, job_position, is_patient
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data["name"],
        data["surname"],
        data["national_id"],
        data["birthdate"],
        data["sex"],
        data["province"],
        data["default_location"],
        data["address"],
        data["phone"],
        data["job_position"],
        True  # Indicating this is a patient
    ))
