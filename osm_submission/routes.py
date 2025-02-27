from flask import Blueprint, request, jsonify
from ..db import get_db


osm_submission_bp = Blueprint('record', __name__)

@osm_submission_bp.route('/record/get_patient_summary', methods=['GET'])
def get_patient_record():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    db, cursor = get_db()
    cursor.execute('''

    '''
    , )

