import db
import json
from decimal import Decimal

def get_table(channel,province):
    # Establish database connection
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            if not province:
                query_ai = """
                SELECT 
                    ai_prediction_mapping.ai_prediction, 
                    COUNT(sr.ai_prediction) AS N
                FROM 
                    (SELECT 0 AS ai_prediction UNION ALL
                    SELECT 1 UNION ALL
                    SELECT 2) AS ai_prediction_mapping
                LEFT JOIN 
                    submission_record sr 
                    ON sr.channel = %s AND sr.ai_prediction = ai_prediction_mapping.ai_prediction
                GROUP BY 
                    ai_prediction_mapping.ai_prediction
                ORDER BY 
                    ai_prediction_mapping.ai_prediction ASC;
                """
                cursor.execute(query_ai, (channel,))
                ai_predict_query = cursor.fetchall()
                total_pic = sum(value for key, value in ai_predict_query)
                ai_predict = mapAiPrediction(ai_predict_query)
                
                query_dent = """
                SELECT 
                    dentist_feedback_code_mapping.dentist_feedback_code, 
                    COALESCE(SUM(submission_counts.N), 0) AS N
                FROM 
                    (SELECT 'OSCC' AS dentist_feedback_code
                    UNION ALL
                    SELECT 'OPMD' 
                    UNION ALL
                    SELECT 'Normal' 
                    UNION ALL
                    SELECT 'BAD_IMG' 
                    UNION ALL
                    SELECT 'OTHER' 
                    UNION ALL
                    SELECT 'Not_diagnosed') AS dentist_feedback_code_mapping
                LEFT JOIN 
                    (SELECT 
                        dentist_feedback_code, 
                        COUNT(*) as N
                    FROM 
                        submission_record sr 
                    WHERE 
                        sr.channel = %s
                    GROUP BY 
                        sr.dentist_feedback_code) AS submission_counts
                    ON dentist_feedback_code_mapping.dentist_feedback_code = submission_counts.dentist_feedback_code
                    OR (dentist_feedback_code_mapping.dentist_feedback_code = 'Not_diagnosed'
                        AND submission_counts.dentist_feedback_code IS NULL)
                GROUP BY 
                    dentist_feedback_code_mapping.dentist_feedback_code;
                """
                cursor.execute(query_dent, (channel,))
                dentist_diagnose_query = cursor.fetchall()

                query_ai_correct = """
                SELECT
                ai_prediction,
                dentist_feedback_code
                FROM
                submission_record sr
                WHERE
                channel = %s
                AND dentist_feedback_code is not null
                AND dentist_feedback_code in ('Normal','OPMD','OSCC')
                """
                cursor.execute(query_ai_correct, (channel,))
                ai_correct_query = cursor.fetchall()
                true_predict = calculateTruePredict(ai_correct_query)
                sum_dent_diagnose = sum(value for key, value in dentist_diagnose_query)
                accuracy = Decimal(true_predict/sum_dent_diagnose*100).quantize(Decimal('0.01'))
                dentist_diagnose = mapDentDiagnosis(dentist_diagnose_query)
            else: 
                query_ai = """
                SELECT 
                    ai_prediction_mapping.ai_prediction, 
                    COUNT(sr.ai_prediction) AS N
                FROM 
                    (SELECT 0 AS ai_prediction UNION ALL
                    SELECT 1 UNION ALL
                    SELECT 2) AS ai_prediction_mapping
                LEFT JOIN 
                    submission_record sr 
                    ON sr.channel = %s
                    AND sr.ai_prediction = ai_prediction_mapping.ai_prediction
                    AND sr.location_province = %s
                GROUP BY 
                    ai_prediction_mapping.ai_prediction
                ORDER BY 
                    ai_prediction_mapping.ai_prediction ASC;
                """
                cursor.execute(query_ai, (channel,province,))
                ai_predict_query = cursor.fetchall()
                total_pic = sum(value for key, value in ai_predict_query)
                ai_predict = mapAiPrediction(ai_predict_query)

                query_dent = """
                SELECT 
                    dentist_feedback_code_mapping.dentist_feedback_code, 
                    COALESCE(SUM(submission_counts.N), 0) AS N
                FROM 
                    (SELECT 'OSCC' AS dentist_feedback_code
                    UNION ALL
                    SELECT 'OPMD' 
                    UNION ALL
                    SELECT 'Normal' 
                    UNION ALL
                    SELECT 'BAD_IMG' 
                    UNION ALL
                    SELECT 'OTHER' 
                    UNION ALL
                    SELECT 'Not_diagnosed') AS dentist_feedback_code_mapping
                LEFT JOIN 
                    (SELECT 
                        dentist_feedback_code, 
                        COUNT(*) as N
                    FROM 
                        submission_record sr 
                    WHERE 
                        sr.channel = %s
                        AND sr.location_province = %s
                    GROUP BY 
                        sr.dentist_feedback_code) AS submission_counts
                    ON dentist_feedback_code_mapping.dentist_feedback_code = submission_counts.dentist_feedback_code
                    OR (dentist_feedback_code_mapping.dentist_feedback_code = 'Not_diagnosed'
                        AND submission_counts.dentist_feedback_code IS NULL)
                GROUP BY 
                    dentist_feedback_code_mapping.dentist_feedback_code;
                """
                cursor.execute(query_dent, (channel,province,))
                dentist_diagnose_query = cursor.fetchall()

                query_ai_correct = """
                SELECT
                ai_prediction,
                dentist_feedback_code
                FROM
                submission_record sr
                WHERE
                channel = %s
                AND location_province = %s
                AND dentist_feedback_code is not null
                AND dentist_feedback_code in ('Normal','OPMD','OSCC')
                """
                cursor.execute(query_ai_correct, (channel,province,))
                ai_correct_query = cursor.fetchall()
                true_predict = calculateTruePredict(ai_correct_query)
                sum_dent_diagnose = sum(value for key, value in dentist_diagnose_query)
                accuracy = Decimal(true_predict/sum_dent_diagnose*100).quantize(Decimal('0.01'))
                dentist_diagnose = mapDentDiagnosis(dentist_diagnose_query)
            # Format Output
            output = {}
            output['ai_predict'] = ai_predict
            output['dentist_diagnose'] = dentist_diagnose
            output['total_pic'] = total_pic
            output['accuracy'] = accuracy
    except Exception as e:
        # Handle Errors
        return json.dumps({"error": str(e)}), 500
    
    finally:
        # Close Connection
        connection.close()
    
    # Return Output
    return output

def mapAiPrediction(prediction):
    prediction_mapping = {
        0: "normal",
        1: "opmd",
        2: "oscc"
    }
    mapped_predictions = {
        prediction_mapping[item[0]]: item[1] for item in prediction
    }
    return mapped_predictions

def mapDentDiagnosis(diagnosis):
    diagnosis_mapping = {
        "OSCC": "oscc",
        "OPMD": "opmd",
        "Normal": "normal",
        "BAD_IMG": "poor_image",
        "OTHER":"others",
        "Not_diagnosed": "not_diagnosed"
        }
    mapped_diagnosis = {
        diagnosis_mapping[item[0]]: int(item[1]) for item in diagnosis
    }
    return mapped_diagnosis

def calculateDentAgree(dent_diagnosis,dent_agree):
    prediction_mapping = {
    0: "Normal",
    1: "OPMD",
    2: "OSCC"
    }

    result = {key: value for key, value in dent_diagnosis}

    for feedback_code, prediction_index, count in dent_agree:
        mapped_prediction = prediction_mapping[prediction_index]  # Map prediction index to name
        if mapped_prediction in result:
            result[mapped_prediction] += Decimal(count)  # Add the count
        else:
            result[mapped_prediction] = Decimal(count)  # Add new key if not present

    result_tuple = tuple((key, value) for key, value in result.items())
    return result_tuple

def calculateTruePredict(input_data):
    true_predict =0
    mapping = {
        0: "Normal",
        1: "OPMD",
        2: "OSCC"
    }

    for predicted_class, expected_class in input_data:
        predicted_label = mapping.get(predicted_class, None)
   
        if predicted_label == expected_class:
            true_predict += 1
    return true_predict