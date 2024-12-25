from . import post_patient , get_patient_oralcancer , post_doctor


def register_patient(data):
    output = post_patient.post_patient(data)
    return output

def register_doctor(data):
    output = post_doctor.post_doctor(data)
    return output

def oralcancer_patient(id):
    output = get_patient_oralcancer.get_data_oralcancer(id)
    return output
