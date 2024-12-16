from flask import json,jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
import db

def verify_by_username_password(username, password):
    query = "SELECT * FROM user WHERE username = %s"
    user, error = get_user_by_query(query, (username,))
    
    if error:
        return jsonify({"error": error}), 500
    if user is None:
        return jsonify({"error": "Invalid username"}), 401
    
    if check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['id']), additional_claims=user)  # Use user ID as the identity
        return jsonify({"access_token": access_token, "message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid password"}), 401

def verify_by_thid_mobile(thid, mobile):
    query = "SELECT * FROM user WHERE national_id = %s AND phone = %s"
    user, error = get_user_by_query(query, (thid, mobile))

    if error:
        return jsonify({"error": error}), 500
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user['id']), additional_claims=user)  # Use user ID as the identity
    return jsonify({"access_token": access_token, "message": "Login successful"}), 200

def get_user_by_query(query, params):
    connection, cursor = db.get_db()
    try:
        cursor.execute(query, params)
        user = cursor.fetchone()
        if user is None:
            return None, "User not found"
        return user, None  # return the user and None for no error
    except Exception as e:
        return None, f"Error retrieving user: {str(e)}"
    finally:
        db.close_db()
