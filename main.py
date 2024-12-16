import os
from flask import Flask, jsonify, request
from login import login_bp
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager


# Create Flask app instance
app = Flask(__name__, instance_relative_config=True)
CORS(app)

# Load configuration from file
app.config.from_pyfile('config.py', silent=True)  # load the instance config

# Configure JWT token
app.config["JWT_SECRET_KEY"] = "your-secure-secret-key"  # Set a secret key directly here
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)  # Initialize JWTManager

### Swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "AIDOC API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### End Swagger specific ###

# Register Blueprints
app.register_blueprint(login_bp, url_prefix='/')

app.json.ensure_ascii = False

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import decode_token, get_jwt_identity, JWTManager
from werkzeug.exceptions import Unauthorized

# Initialize JWT Manager (Make sure this is set up in your app)
jwt = JWTManager()

# # Custom decorator to enforce JWT in request header
# def token_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # Extract the token from the Authorization header
#         auth_header = request.headers.get('Authorization')

#         if not auth_header:
#             return jsonify({"error": "Authorization token is missing"}), 401

#         try:
#             # The token comes in the format: "Bearer <token>"
#             token = auth_header.split(" ")[1]
#         except IndexError:
#             return jsonify({"error": "Authorization token malformed"}), 401

#         try:
#             # Decode the token and verify it
#             decoded_token = decode_token(token)
#             current_user = get_jwt_identity()  # Get the user identity from the token
#         except Exception as e:
#             return jsonify({"error": f"Token is invalid: {str(e)}"}), 401

#         # You can assign the decoded information to `request` for future use if needed
#         request.user = current_user
        
#         # Continue to the route handler
#         return f(*args, **kwargs)
    
#     return decorated_function

    
if __name__ == '__main__':
    app.run(debug=True)
