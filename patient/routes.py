from flask import request, Blueprint, jsonify
from .patient_edit import get_user_info, update_user_info

patient_edit_bp = Blueprint('login', __name__)


@patient_edit_bp.route('/patient/edit/', methods=['GET'])
def get_patient_info():
    try:
        user_id = request.args.get("user_id")
        if not user_id:  return jsonify({"error": "User id not provided"}), 400
        
        return get_user_info(user_id)

    except Exception as e:
        return jsonify({"error": f"an error occurred: {str(e)}"}), 500


@patient_edit_bp.route('/patient/edit/', methods=['PUT'])
def edit_patient_info():
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        fields = [
            ('name', data.get("name")),
            ('surname', data.get("surname")),
            ('job_position', data.get("job")),
            ('province', data.get("province")),
            ('email', data.get("email")),
            ('phone', data.get("phone"))
        ]
        
        if not user_id:  return jsonify({"error": "No or missing fields."}), 400
        
        return update_user_info(user_id, fields)
        
        
        
    except Exception as e:
        return jsonify({"error": f"an error occurred: {str(e)}"}), 500
    
