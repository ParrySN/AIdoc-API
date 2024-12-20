from . import post_patient , get_patient_oralcancer


def post_register_patient(data):
    output = post_patient.post_patient(data)
    return output

def get_oralcancer_patient(id):
    output = get_patient_oralcancer.get_data_oralcancer(id)
    return output