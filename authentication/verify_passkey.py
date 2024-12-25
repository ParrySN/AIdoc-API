from flask import json,jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from common.common_mapper import map_role_to_list
import db

def verify_by_username_password(username, password):
    try:
        query = "SELECT * FROM user WHERE username = %s"
        user, error = get_user_by_query(query, (username,))
        role = map_role_to_list(user)

        if user is None:
            return jsonify({"error": "Invalid username"}), 401
        
        if check_password_hash(user['password'], password):
            access_token = create_access_token(identity=str(role), additional_claims=user)
            return jsonify({"access_token": access_token, "message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401
    except Exception as e:
        return {"message": str(e)}, 500

def verify_by_thid_mobile(thid, mobile):
    try:
        query = "SELECT * FROM user WHERE national_id = %s AND phone = %s"
        user, error = get_user_by_query(query, (thid, mobile))
        role = map_role_to_list(user)

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=str(role), additional_claims=user)
        return jsonify({"access_token": access_token, "message": "Login successful"}), 200
    except Exception as e:
        return {"message": str(e)}, 500

def get_user_by_query(query, params):
    connection, cursor = db.get_db()
    try:
        cursor.execute(query, params)
        user = cursor.fetchone()
        if user is None:
            return None, "User not found"
        return user, None  
    except Exception as e:
        return None, f"Error retrieving user: {str(e)}"
