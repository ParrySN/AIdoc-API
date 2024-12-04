from flask import jsonify, request, Blueprint
import db
from admin import admin

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin_page/', methods=['GET'])
def get_admin_page():
    return admin.generate_admin_page()

@admin_bp.route('/edit_user_info/', methods=['GET'])
def get_edit_user():
    id = request.args.get('id')
    output = admin.generate_user_edit_info(id)
    return output

@admin_bp.route('/delete_user/', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    
    if not data or 'id' not in data:
        return jsonify({'error': 'No user ID provided'}), 400  
    
    user_id = data['id']
    
    output = admin.delete_user(user_id)
    
    return output

from flask import request, jsonify

@admin_bp.route('/submit_info/', methods=['PUT'])
def put_submit_edited_info():
    data = request.get_json()

    required_fields = [
        "name", "surname", "job_position", "is_patient", "is_osm", 
        "is_specialist", "is_admin", "email", "province", "national_id", 
        "hospital", "phone"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    output = admin.put_update_user_info(data)

    return output


