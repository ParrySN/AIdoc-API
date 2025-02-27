from flask import Blueprint, request, jsonify
from db import get_db
from flask_jwt_extended import jwt_required

osm_submission_bp = Blueprint('osm_record', __name__)

@osm_submission_bp.route('/record/get_patient_summary', methods=['GET'])
@jwt_required()
def get_patient_record():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    db, cursor = get_db()
    cursor.execute('''
        SELECT 
            SUM(dentist_feedback_code = 'NORMAL') AS normal_count,
            SUM(dentist_feedback_code = 'BAD_IMG') AS bad_img_count,
            SUM(dentist_feedback_code IN ('OSCC', 'OPMD', 'BENIGN')) AS diagnosised_count,
            SUM(dentist_feedback_code NOT IN ('NORMAL', 'BAD_IMG', 'OSCC', 'OPMD', 'BENIGN') OR dentist_feedback_code IS NULL) AS waiting_count,
            COUNT(*) AS total
        FROM submission_record
        WHERE sender_id = %s;
    ''', (user_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "not found"}), 404
    
    return jsonify(result), 200


@osm_submission_bp.route('/user/get_patient', methods=['GET'])
@jwt_required()
def get_patient_list():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    db, cursor = get_db()
    cursor.execute('''
        SELECT DISTINCT u.name, u.surname, u.sex, u.address
        FROM submission_record sr
        LEFT JOIN user u ON u.id = sr.patient_id
        WHERE sr.patient_id is not NULL AND sr.sender_id = %s;
    ''', (user_id,))
    result = cursor.fetchall()

    return jsonify(result if result else [] ), 200
