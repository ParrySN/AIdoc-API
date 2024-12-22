from flask import Blueprint , request ,jsonify
from . import register

register_bp = Blueprint('register', __name__)
@register_bp.route("/register/patient/", methods=["POST"])
def post_register_patient():
    data = request.get_json()

    required_fields = [
        "name","surname","national_id","birthdate","sex","province"
            ,"default_location","address","phone","job_position"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400


    output = register.post_register_patient(data)

    return output

@register_bp.route("/register/patient/oralcancer/", methods=['GET'])
def get_patient():
    id = request.args.get('id')
    return register.get_oralcancer_patient(id)
    
    