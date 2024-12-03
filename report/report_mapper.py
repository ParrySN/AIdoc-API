from collections import defaultdict


def map_ai_prediction(predictions):
    prediction_mapping = {0: "normal", 1: "opmd", 2: "oscc"}
    return {prediction_mapping.get(item[0], "unknown"): item[1] for item in predictions}

def map_dentist_diagnosis(diagnoses):
    diagnosis_mapping = {
        "OSCC": "oscc", "OPMD": "opmd", "Normal": "normal",
        "BAD_IMG": "poor_image", "OTHER": "others", "Not_diagnosed": "not_diagnosed"
    }
    return {diagnosis_mapping.get(item[0], "unknown"): int(item[1]) for item in diagnoses}

def map_query_to_output_specialist(ai_predict_query, dentist_diagnose_query):
    prediction_mapping = {
        0: "normal",
        1: "opmd",
        2: "oscc"
    }

    ai_predict = defaultdict(lambda: {"normal": 0, "opmd": 0, "oscc": 0})
    total_pics = defaultdict(int)

    for specialist, pred_key, score in ai_predict_query:
        label = prediction_mapping[pred_key]
        ai_predict[specialist][label] += int(score)
        total_pics[specialist] += int(score)

    dentist_diagnose = defaultdict(lambda: {"agree": 0, "disagree": 0})

    for specialist, diag, score in dentist_diagnose_query:
        if diag is None:
            continue
        diag = diag.lower()
        dentist_diagnose[specialist][diag] += int(score)

    total_ai_predict = {"normal": 0, "opmd": 0, "oscc": 0}
    total_dentist_diagnose = {"agree": 0, "disagree": 0}
    total_total_pic = 0

    output = []

    for specialist in set(ai_predict.keys()).union(dentist_diagnose.keys()):
        specialist_data = {
            "job": specialist,
            "ai_predict": ai_predict[specialist],
            "dentist_diagnose": dentist_diagnose[specialist],
            "total_pic": total_pics[specialist]
        }
        output.append(specialist_data)

        for key in total_ai_predict:
            total_ai_predict[key] += ai_predict[specialist][key]
        for key in total_dentist_diagnose:
            total_dentist_diagnose[key] += dentist_diagnose[specialist][key]
        total_total_pic += total_pics[specialist]

    output.append({
        "job": "total",
        "ai_predict": total_ai_predict,
        "dentist_diagnose": total_dentist_diagnose,
        "total_pic": total_total_pic
    })
    return output