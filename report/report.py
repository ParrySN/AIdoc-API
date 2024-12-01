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
        'account_status': {}
    }
    # try:
    #     # Attempt to compute and update the total predictions and accuracy
    #     output['patient_and_osm']['total']['ai_predict'] = sum_dicts(osm['ai_predict'], patient['ai_predict'])
    #     output['patient_and_osm']['total']['dentist_diagnose'] = sum_dicts(osm['dentist_diagnose'], patient['dentist_diagnose'])
        
    #     # Compute the average accuracy
    #     accuracy_values = [
    #         Decimal(osm["accuracy"]),
    #         Decimal(patient["accuracy"])
    #     ]
    #     total_accuracy = sum(accuracy_values) / len(accuracy_values)
    #     output['patient_and_osm']['total']['accuracy'] = f"{total_accuracy:.2f}"  # Format to 2 decimal places
    # except Exception as e:
    #     # Log the exception for debugging (optional)
    #     print(f"Error occurred: {e}")
    
    #     # Return error response
    #     return make_response(jsonify({
    #         "status": "error",
    #         "message": "Invalid request parameters."
    #     }), 400)

    
    # Return the JSON output
    return jsonify(output)

def sum_dicts(dict1, dict2):
    result = {}
    for key in dict1:
        if isinstance(dict1[key], dict): 
            result[key] = sum_dicts(dict1[key], dict2[key])
        else:  
            result[key] = dict1[key] + dict2[key]
    return result











