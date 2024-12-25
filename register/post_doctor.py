import db
from flask import json
from . import get_patient_oralcancer

def post_doctor(data):
    connection, cursor = db.get_db()
    try:
        # Check if the national_id already exists
        # if check_username_exists(cursor, data["username"]):
        #     return json.dumps({
        #         "error": "This username already exist"
        #     }), 400

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


# def check_username_exists(cursor, username):
#     sql = "SELECT 1 FROM user WHERE username = %s"
#     cursor.execute(sql, (username,))
#     return cursor.fetchone() is not None


def post_table_user(cursor, data):
    print("in")
    sql = """
        INSERT INTO user (
            name, surname, email, phone, sex , username, password,
            province, hospital, address, job_position
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(sql, (
        data["name"],
        data["surname"],
        data["email"],
        data["phone"],
        data["sex"],
        data["username"],
        data["password"],
        data["province"],
        data["hospital"],
        data["address"],
        data["job_position"],
    ))