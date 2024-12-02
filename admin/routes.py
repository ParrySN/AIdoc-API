from flask import jsonify, request, Blueprint
import db
from admin import admin

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin_page/', methods=['GET'])
def GetAdminPage():
    return admin.getAdminPage()

@admin_bp.route('/edit_user_info/', methods=['GET'])
def EditUser():
    id = request.args.get('id')
    output = admin.getUserEditInfo(id)
    return output

@admin_bp.route('/delete_user/', methods=['DELETE'])
def DeleteUser():
    data = request.get_json()
    
    if not data or 'id' not in data:
        return jsonify({'error': 'No user ID provided'}), 400  
    
    user_id = data['id']
    
    output = admin.deleteUser(user_id)
    
    return output

from flask import request, jsonify

@admin_bp.route('/submit_info/', methods=['PUT'])
def submitEditedInfo():
    # Get the JSON data from the request body
    data = request.get_json()

    # Check if all required fields are in the request data
    required_fields = [
        "name", "surname", "job_position", "is_patient", "is_osm", 
        "is_specialist", "is_admin", "email", "province", "national_id", 
        "hospital", "phone"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    output = admin.updateUserInfo(data)

    return output

