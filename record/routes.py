from flask import Blueprint, request, jsonify
from .patientRecord import get_patient_records

record_bp = Blueprint('record', __name__)

@record_bp.route('/record', methods=['GET'])
def get_patient_record():
    key = request.args.get('key')

    if not key:
        return jsonify({"message": "key is required"}), 400

    # Check user in aidoc_development database
    result, status = get_patient_records(key)
    if result:
        return result, status

    return jsonify({"message": "record not found"}), 404
