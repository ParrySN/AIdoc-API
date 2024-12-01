import json
import db
from report import get_account_status, get_all_submission, get_table_by_channel
from report import get_table_by_channel_dentist
from flask import jsonify, make_response
from decimal import Decimal

def report(role, province):
    patient = get_table_by_channel.get_table("PATIENT",province)
    osm = get_table_by_channel.get_table("OSM",province)

    dentist = get_table_by_channel_dentist.get_table(province)

    total_pic = get_all_submission.get_all_submission(province)

    output = {
        'status': 'success',
        'patient_and_osm':{
            'patient': patient,
            'osm': osm,
            'total': {
            "accuracy" : "-", 
            "ai_predict": {
                "normal": 0,
                "opmd": 0,
                "oscc": 0
            },
            "dentist_diagnose": {
                "agree": 0,
                "disagree": 0
            },
            "total_pic": 0
        }
        },
        'province': province,
        'specialist': dentist,
        'total_pic': total_pic,
    }

    try:
        output['patient_and_osm']['total']['ai_predict'] = sum_dicts(osm['ai_predict'], patient['ai_predict'])
        output['patient_and_osm']['total']['dentist_diagnose'] = sum_dicts(osm['dentist_diagnose'], patient['dentist_diagnose'])

        accuracy_values = []
        accuracy_divider = 0

        if osm["accuracy"] != "-":
            accuracy_values.append(Decimal(osm["accuracy"]))
            accuracy_divider += 1
        else:
            accuracy_values.append(Decimal(0))  # Add 0 if accuracy is missing

        if patient["accuracy"] != "-":
            accuracy_values.append(Decimal(patient["accuracy"]))
            accuracy_divider += 1
        else:
            accuracy_values.append(Decimal(0))  # Add 0 if accuracy is missing

        # Compute total accuracy by averaging valid accuracy values
        if accuracy_divider > 0:
            total_accuracy = sum(accuracy_values) / accuracy_divider
            output['patient_and_osm']['total']['accuracy'] = f"{total_accuracy:.2f}"  # Format to 2 decimal places
        else:
            # In case no valid accuracy values are provided, set accuracy to "-"
            output['patient_and_osm']['total']['accuracy'] = "-"
    except Exception as e:
        print(f"Error occurred while calculating total: {e}")

        # Set default values in case of error
        output['patient_and_osm']['total'] = {
            "ai_predict": {
                "normal": 0,
                "opmd": 0,
                "oscc": 0
            },
            "dentist_diagnose": {
                "normal": 0,
                "not_diagnosed": 0,
                "opmd": 0,
                "oscc": 0,
                "others": 0,
                "poor_image": 0
            },
            "accuracy": "-"
        }

    return jsonify(output)

def sum_dicts(dict1, dict2):
    result = {}
    for key in dict1:
        if isinstance(dict1[key], dict): 
            result[key] = sum_dicts(dict1[key], dict2[key])
        else:  
            result[key] = dict1[key] + dict2[key]
    return result











