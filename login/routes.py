from flask import request, Blueprint, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .verify_passkey import verify_by_username_password, verify_by_thid_mobile
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt

login_bp = Blueprint('login', __name__)

@login_bp.route('/verify/passkey/', methods=['GET'])
def verify_passkey():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        thid = request.args.get("thid")
        mobile = request.args.get("mobile")

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

@login_bp.route('/get_user/', methods=['GET'])
@jwt_required()
def hash_password():
    
    # Retrieve the entire user data from the JWT claims
    claims = get_jwt()
    
    # The full user data is stored in the claims dictionary
    user_data = claims 
    
    # Return response with current user data and hashed password
    return jsonify(user_data), 200

