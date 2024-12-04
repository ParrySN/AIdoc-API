from flask import json
from werkzeug.security import check_password_hash
import db

def verify_by_username_password(username, password):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT username, password FROM user WHERE username = %s"""
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            
            if not user: return json.dumps({"error": "invalid credential"}), 401
            
            hashed_password = user[1]
            if check_password_hash(hashed_password, password):
                return json.dumps({"message": "valid credential."}), 200
            
            return json.dumps({"error": "invalid password."}), 401

    except Exception as e:
        return json.dumps({"error": f"an error occurred while verifying passkey by username and password: {str(e)}"}), 500
    
    finally:
        connection.close()


def verify_by_thid_mobile(thid, mobile):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = """SELECT national_id, phone FROM user WHERE national_id = %s AND phone = %s"""
            cursor.execute(sql, (thid, mobile))
            user = cursor.fetchone()

            if not user: return json.dumps({"error": "invalid credential"}), 401

            return json.dumps({"message": "valid credential."}), 200

    except Exception as e:
        return json.dumps({"error": f"an error occurred while verifying passkey by thid and mobile: {str(e)}"}), 500
    
    finally:
        connection.close()
