from datetime import timedelta
import os
from flask import Flask, jsonify
import db
from authentication import authentication_bp
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager
# from products import products_bp


app = Flask(__name__, instance_relative_config=True)
CORS(app) 

# load the instance config
app.config.from_pyfile('config.py', silent=True) 

# Configure JWT token
app.config["JWT_SECRET_KEY"] = app.config.get('SECRET_KEY', 'SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_BLOCKLIST_ENABLED'] = True
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

jwt = JWTManager(app)

# Blocklist check (Middleware)
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    connection, cursor = db.get_db()
    try:
        with cursor:
            query = "SELECT token FROM jwt_blocklist WHERE token = %s"
            cursor.execute(query, (jwt_payload['jti'],))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Error checking blocklist: {e}")

### Swagger Configure ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "AIDOC API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# Register Blueprints
app.register_blueprint(authentication_bp, url_prefix='/')

app.json.ensure_ascii=False

if __name__ == '__main__':
    app.run(debug=True)