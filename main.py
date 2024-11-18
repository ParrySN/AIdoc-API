from flask import Flask
from report import report_bp
# from products import products_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(report_bp, url_prefix='/')
# app.register_blueprint(users_bp, url_prefix='/')
# app.register_blueprint(products_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)