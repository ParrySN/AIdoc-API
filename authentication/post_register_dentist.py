import common.common_util as cu
import db
from flask import json

def post_dentist(data):
    connection, cursor = db.get_db()
    try:
        if check_username_exists(cursor, data["username"]):
            return json.dumps({
                "error": "Account with this username already exist"
            }), 409
        
        valid_phone, message = cu.validate_phone(data["phone"])
        if not valid_phone:
            return json.dumps({
                    "error": message
                }), 400
            
        valid_license, message = cu.validate_license(data["license"])
        if not valid_license:
            return json.dumps({
                    "error": message
                }), 400
        
        valid_email, message = cu.validate_email(data["email"])
        if not valid_email:
            return json.dumps({
                    "error": message
                }), 400
        
        confirm_email, message = cu.confirm_input(data["email"], data["confirm_email"], "อีเมล")
        if not confirm_email:
            return json.dumps({
                "error": message
            }), 400
        
        confirm_password, message = cu.confirm_input(data["password"], data["confirm_password"], "รหัสผ่าน")
        if not confirm_password:
            return json.dumps({
                "error": message
            }), 400
        post_dentist_query(cursor, data)
            
        output = {
            "message": "Post successfully",
            "doctor_data": data
        }
    except Exception as e:
        return json.dumps({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

    return output


def check_username_exists(cursor, username):
    sql = "SELECT * FROM user WHERE username = %s"
    cursor.execute(sql, (username,))
    return cursor.fetchone() is not None


def post_dentist_query(cursor, data):
    sql = """
        INSERT INTO user (
        name, surname, email, phone, license,
        username, password, province, hospital, job_position, last_login
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    cursor.execute(sql, (
        data["name"],
        data["surname"],
        data["email"],
        data["phone"],
        data["license"],
        data["username"],
        data["password"],
        data["province"],
        data["hospital"],
        data["job_position"],
    ))
