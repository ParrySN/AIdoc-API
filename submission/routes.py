from flask import request, Blueprint, jsonify
from .get_submission import get_submission_by_role

submission_bp = Blueprint('submission', __name__)


@submission_bp.route('/record/get_by_role/', methods=['GET'])
def get_record():
    try:
        roles = {"admin", "patient", "osm", "dentist" }
        role = request.args.get("role")
        user_id  = request.args.get("user_id")

        if (role in roles): return get_submission_by_role(role, int(user_id))
        else: return jsonify({"error": "invalid role."}), 400
        
    except Exception as e:
        return jsonify({"error": f"an error occurred: {str(e)}"}), 500
