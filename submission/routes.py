from flask import jsonify, request, Blueprint
import db
from submission import submission

submission_bp = Blueprint('submission', __name__)

@submission_bp.route('/record/init', methods=['POST'])
def create_record():
    data = request.get_json()
    imageList = request.files.getlist("imageList")
    required_fields = [
        "channel", "fname", "sender_id", "sender_phone", "zip_code", 
        "patient_id", "patient_national_id", "ai_prediction", "ai_scores", "dentist_id", 
        "dentist_feedback_code", "dentist_feedback_comment", "dentist_feedback_lesion", "dentist_feedback_location",
        "dentist_feedback_date","is_submit","is_rotate"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    return submission.generate_record(data,imageList)