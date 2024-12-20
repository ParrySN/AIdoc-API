from flask import Flask
from report import report_bp
from register import register_bp
from flask_swagger_ui import get_swaggerui_blueprint
# from products import products_bp

app = Flask(__name__)

# Register Blueprints
# app.register_blueprint(report_bp, url_prefix='/')
# app.register_blueprint(users_bp, url_prefix='/')
# app.register_blueprint(products_bp, url_prefix='/api')

app.config.from_pyfile('configs.py',silent=True)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "AIDOC API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT,url_prefix=SWAGGER_URL)
app.register_blueprint(register_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)