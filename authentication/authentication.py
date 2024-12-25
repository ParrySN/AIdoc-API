from flask import jsonify
from flask_jwt_extended import get_jwt

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
    connection, cursor = db.get_db()
    try:
        with cursor:
            query = "INSERT INTO jwt_blocklist (token) VALUES (%s)"
            cursor.execute(query, (jti,))
        return jsonify({"msg": "Successfully logged out"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500