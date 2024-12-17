import os
from flask import Flask, jsonify
from report import report_bp
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
# from products import products_bp


app = Flask(__name__, instance_relative_config=True)
CORS(app) 

app.config.from_pyfile('config.py', silent=True) # load the instance config

### swagger specific ###
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
### end swagger specific ###

# Register Blueprints
app.register_blueprint(report_bp, url_prefix='/')

app.json.ensure_ascii=False

if __name__ == '__main__':
    app.run(debug=True)