def map_ai_prediction_list(predictions):
    prediction_mapping = {0: "normal", 1: "opmd", 2: "oscc"}
    return {prediction_mapping.get(item[0], "unknown"): item[1] for item in predictions}

def map_dentist_diagnosis(diagnoses):
    diagnosis_mapping = {
        "OSCC": "oscc", "OPMD": "opmd", "Normal": "normal",
        "BAD_IMG": "poor_image", "OTHER": "others", "Not_diagnosed": "not_diagnosed"
    }
    return {diagnosis_mapping.get(item[0], "unknown"): int(item[1]) for item in diagnoses}
