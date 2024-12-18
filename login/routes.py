from flask import Blueprint, request, jsonify
from .login import verify_user_from_aidoc, verify_user_from_questionnaire
import jwt

login_bp = Blueprint('login', __name__)

@login_bp.route('/verify/user', methods=['GET'])
def verify_user():
    key = request.args.get('key')

    if not key:
        return jsonify({"message": "key is required"}), 400

    # Check user in aidoc_development database
    result, status = verify_user_from_aidoc(key)
    if result:
        return jsonify(result), status

    # Check user in oralcancer database
    result, status = verify_user_from_questionnaire(key)
    if result:
        return jsonify(result), status

    return jsonify({"message": "user not found"}), 401