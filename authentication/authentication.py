from flask import jsonify, request
from flask_jwt_extended import get_jwt, decode_token

from authentication import post_register_dentist, post_register_osm, post_register_patient
from authentication.verify_passkey import verify_by_thid_mobile, verify_by_username_password
import db
from .verify_user import verify_user_from_aidoc, verify_user_from_questionnaire

def check_user_channel(key):
    result, status = verify_user_from_aidoc(key)
    if result:
        return jsonify(result), status

    result, status = verify_user_from_questionnaire(key)
    if result:
        return jsonify(result), status

    return jsonify({"message": "user not found"}), 401

def login_with_passkey(username, password, thid, mobile):
    try:
        if username and password and not (thid or mobile):
            output = verify_by_username_password(username, password)

        elif thid and mobile and not (username or password):
            output = verify_by_thid_mobile(thid, mobile)
        else:
            return jsonify({
                "error": "Invalid request format. Provide either username/password or thid/mobile."
            }), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    return output

def revoke_token(): 
    jti = get_jwt()['jti']
    user_id = get_jwt()['id']
    connection, cursor = db.get_db()
    try:
        with cursor:
            query = """
            UPDATE access_token
            SET is_revoke = TRUE, 
            update_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND jti = %s
            """
            cursor.execute(query, (user_id, jti))
        
        connection.commit() 
        return jsonify({"msg": "Successfully logged out"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
def register_patient(data):
    required_fields = [
        "name","surname","national_id","birthdate","sex","province"
            ,"district","subdistrict","address","phone","job_position","zipcode","confirm_national_id"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    output = post_register_patient.post_patient(data)

    return output

def register_dentist(data):
    required_fields = [
        "name","surname","job_position","hospital","province","phone","license"
        ,"email","username","password","confirm_password","confirm_email"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    output = post_register_dentist.post_dentist(data)

    return output

def register_osm(data):
    required_fields = [
        "name","surname","job_position","hospital","province","national_id","phone"
        ,"confirm_national_id","confirm_phone"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400


    output = post_register_osm.post_osm(data)

    return output

def risk_oca_status():
    claims = get_jwt()
    print(claims)
    user_id = claims['id']
    name = claims['name']
    surname = claims['surname']
    db.close_db()
    connection, cursor = db.get_db_2()
    try:
        with cursor:
            query = """
            SELECT 
                *
            FROM 
                questionnaire
            WHERE 
                cid = %s
                OR (
                    name LIKE %s
                    AND name LIKE %s
                )
            ORDER BY id DESC
            """
            cursor.execute(query, (user_id, f"%{name}%", f"%{surname}%"))
            result = cursor.fetchone()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close_db()
    return jsonify(result), 200
