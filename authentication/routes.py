from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required,jwt_required, get_jwt

from authentication.authentication import check_user_channel, login_with_passkey, revoke_token
import db
from .verify_passkey import verify_by_username_password, verify_by_thid_mobile
import jwt

authentication_bp = Blueprint('authentication', __name__)

@authentication_bp.route('/verify/user', methods=['GET'])
def verify_user():
    key = request.args.get('key')

    if not key:
        return jsonify({"message": "key is required"}), 400
    output = check_user_channel(key)

    return output

@authentication_bp.route('/verify/passkey/', methods=['GET'])
def verify_passkey():
    username = request.args.get("username")
    password = request.args.get("password")
    thid = request.args.get("thid")
    mobile = request.args.get("mobile")

    output = login_with_passkey(username, password, thid, mobile)
    return output

@authentication_bp.route('/get_user/', methods=['GET'])
@jwt_required()
def hash_password():
    
    # Retrieve the entire user data from the JWT claims
    claims = get_jwt()
    
    # The full user data is stored in the claims dictionary
    user_data = claims 
    
    # Return response with current user data and hashed password
    return jsonify(user_data), 200

@authentication_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    output = revoke_token()
    return output