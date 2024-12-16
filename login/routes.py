from flask import request, Blueprint, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from .verify_passkey import verify_by_username_password, verify_by_thid_mobile
from datetime import timedelta

login_bp = Blueprint('login', __name__)

# Configure JWT Secret Key
from flask import Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = current_app.config['']  # Replace with a strong secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)  # Initialize JWT extension

@login_bp.route('/verify/passkey/', methods=['GET'])
def verify_passkey():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        thid = request.args.get("thid")
        mobile = request.args.get("mobile")

        if username and password and not (thid or mobile):
            return verify_by_username_password(username, password)
        
        elif thid and mobile and not (username or password):
            return verify_by_thid_mobile(thid, mobile)
        
        else: return jsonify({"error": "invalid request format. provide either username/password or thid/mobile."}), 400
        
    except Exception as e:
        return jsonify({"error": f"an error occurred: {str(e)}"}), 500


