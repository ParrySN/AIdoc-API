import db
import json
from decimal import Decimal
from collections import defaultdict

def get_table(province):
    # Establish database connection
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            if not province:
                query_ai = """
                SELECT 
                    job_position_mapping.job_position,
                    ai_prediction_mapping.ai_prediction, 
                    COALESCE(SUM(submission_counts.N), 0) AS N
                FROM 
                    (SELECT DISTINCT u.job_position 
                    FROM submission_record sr 
                    LEFT JOIN user u
                    ON u.id = sr.sender_id 
                    WHERE u.job_position IS NOT NULL AND sr.channel = 'DENTIST') AS job_position_mapping
                CROSS JOIN 
                    (SELECT 0 AS ai_prediction
                    UNION ALL
                    SELECT 1
                    UNION ALL
                    SELECT 2) AS ai_prediction_mapping
                LEFT JOIN 
                    (SELECT 
                        u.job_position, 
                        sr.ai_prediction, 
                        COUNT(*) AS N 
                    FROM submission_record sr 
                    LEFT JOIN user u 
                    ON u.id = sr.sender_id 
                    WHERE sr.channel = 'DENTIST'
                    GROUP BY u.job_position, sr.ai_prediction) AS submission_counts
                ON 
                    job_position_mapping.job_position = submission_counts.job_position 
                    AND ai_prediction_mapping.ai_prediction <=> submission_counts.ai_prediction
                GROUP BY 
                    job_position_mapping.job_position, 
                    ai_prediction_mapping.ai_prediction;
                """
                cursor.execute(query_ai)
                ai_predict_query = cursor.fetchall()
                query_dent = """
                SELECT 
                    job_position_mapping.job_position,
                    dentist_feedback_code_mapping.dentist_feedback_code, 
                    COALESCE(SUM(submission_counts.N), 0) AS N
                FROM 
                    (SELECT DISTINCT job_position 
                    FROM submission_record sr 
                    LEFT JOIN
                    user u
                    ON u.id = sr.sender_id 
                    WHERE job_position IS NOT NULL and channel = 'DENTIST') AS job_position_mapping
                CROSS JOIN 
                    (SELECT 'AGREE' AS dentist_feedback_code
                    UNION ALL
                    SELECT 'DISAGREE'
                    UNION ALL
                    SELECT NULL) AS dentist_feedback_code_mapping
                LEFT JOIN 
                    (SELECT 
                        u.job_position, 
                        sr.dentist_feedback_code, 
                        COUNT(*) AS N
                    FROM 
                        submission_record sr
                    LEFT JOIN 
                        user u 
                    ON 
                        u.id = sr.sender_id 
                    WHERE 
                        sr.channel = 'DENTIST'
                    GROUP BY 
                        u.job_position, sr.dentist_feedback_code) AS submission_counts
                ON 
                    job_position_mapping.job_position = submission_counts.job_position 
                    AND dentist_feedback_code_mapping.dentist_feedback_code <=> submission_counts.dentist_feedback_code
                GROUP BY 
                    job_position_mapping.job_position, 
                    dentist_feedback_code_mapping.dentist_feedback_code;
                """
                cursor.execute(query_dent)
                dentist_diagnose_query = cursor.fetchall()
                response = mapQueryToOutput(ai_predict_query,dentist_diagnose_query)
            else: 
                query_ai = """
                SELECT 
                    job_position_mapping.job_position,
                    ai_prediction_mapping.ai_prediction, 
                    COALESCE(SUM(submission_counts.N), 0) AS N
                FROM 
                    (SELECT DISTINCT u.job_position 
                    FROM submission_record sr 
                    LEFT JOIN user u
                    ON u.id = sr.sender_id 
                    WHERE u.job_position IS NOT NULL 
                    AND sr.channel = 'DENTIST' 
                    AND sr.location_province = %s) AS job_position_mapping
                CROSS JOIN 
                    (SELECT 0 AS ai_prediction
                    UNION ALL
                    SELECT 1
                    UNION ALL
                    SELECT 2) AS ai_prediction_mapping
                LEFT JOIN 
                    (SELECT 
                        u.job_position, 
                        sr.ai_prediction, 
                        COUNT(*) AS N 
                    FROM submission_record sr 
                    LEFT JOIN user u 
                    ON u.id = sr.sender_id 
                    WHERE sr.channel = 'DENTIST' 
                    AND sr.location_province = %s
                    GROUP BY u.job_position, sr.ai_prediction) AS submission_counts
                ON 
                    job_position_mapping.job_position = submission_counts.job_position 
                    AND ai_prediction_mapping.ai_prediction <=> submission_counts.ai_prediction
                GROUP BY 
                    job_position_mapping.job_position, 
                    ai_prediction_mapping.ai_prediction;
                """
                cursor.execute(query_ai, (province,province,))
                ai_predict_query = cursor.fetchall()
                # Dentist Prediction Query
                query_dent = """
                SELECT 
                    job_position_mapping.job_position,
                    dentist_feedback_code_mapping.dentist_feedback_code, 
                    COALESCE(SUM(submission_counts.N), 0) AS N
                FROM 
                    (SELECT DISTINCT u.job_position 
                    FROM submission_record sr 
                    LEFT JOIN user u
                    ON u.id = sr.sender_id 
                    WHERE u.job_position IS NOT NULL 
                    AND sr.channel = 'DENTIST' 
                    AND sr.location_province = %s) AS job_position_mapping
                CROSS JOIN 
                    (SELECT 'AGREE' AS dentist_feedback_code
                    UNION ALL
                    SELECT 'DISAGREE'
                    UNION ALL
                    SELECT NULL) AS dentist_feedback_code_mapping
                LEFT JOIN 
                    (SELECT 
                        u.job_position, 
                        sr.dentist_feedback_code, 
                        COUNT(*) AS N
                    FROM 
                        submission_record sr
                    LEFT JOIN 
                        user u 
                    ON 
                        u.id = sr.sender_id 
                    WHERE 
                        sr.channel = 'DENTIST'
                        AND sr.location_province = %s
                    GROUP BY 
                        u.job_position, sr.dentist_feedback_code) AS submission_counts
                ON 
                    job_position_mapping.job_position = submission_counts.job_position 
                    AND dentist_feedback_code_mapping.dentist_feedback_code <=> submission_counts.dentist_feedback_code
                GROUP BY 
                    job_position_mapping.job_position, 
                    dentist_feedback_code_mapping.dentist_feedback_code;
                """
                cursor.execute(query_dent, (province,province,))
                dentist_diagnose_query = cursor.fetchall()
                response = mapQueryToOutput(ai_predict_query,dentist_diagnose_query)
            # Format Output
            output = response
    except Exception as e:
        output = {
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
        # Handle Errors
        return json.dumps({"error": str(e)}), 500
    
    finally:
        # Close Connection
        connection.close()
    
    # Return Output
    return output

def mapQueryToOutput(ai_predict_query, dentist_diagnose_query):
    prediction_mapping = {
        0: "normal",
        1: "opmd",
        2: "oscc"
    }

    ai_predict = defaultdict(lambda: {"normal": 0, "opmd": 0, "oscc": 0})
    total_pics = defaultdict(int)

    # Process AI predictions
    for specialist, pred_key, score in ai_predict_query:
        label = prediction_mapping[pred_key]
        ai_predict[specialist][label] += int(score)
        total_pics[specialist] += int(score)

    # Process dentist diagnoses
    dentist_diagnose = defaultdict(lambda: {"agree": 0, "disagree": 0})

    for specialist, diag, score in dentist_diagnose_query:
        if diag is None:
            continue
        diag = diag.lower()  # Convert to lowercase for key consistency
        dentist_diagnose[specialist][diag] += int(score)

    # Initialize totals
    total_ai_predict = {"normal": 0, "opmd": 0, "oscc": 0}
    total_dentist_diagnose = {"agree": 0, "disagree": 0}
    total_total_pic = 0

    # Prepare the final output
    output = []

    for specialist in set(ai_predict.keys()).union(dentist_diagnose.keys()):
        specialist_data = {
            "job": specialist,
            "ai_predict": ai_predict[specialist],
            "dentist_diagnose": dentist_diagnose[specialist],
            "total_pic": total_pics[specialist]
        }
        output.append(specialist_data)

        # Update totals
        for key in total_ai_predict:
            total_ai_predict[key] += ai_predict[specialist][key]
        for key in total_dentist_diagnose:
            total_dentist_diagnose[key] += dentist_diagnose[specialist][key]
        total_total_pic += total_pics[specialist]

    # Append totals as the last element in the array
    output.append({
        "specialist": "total",
        "ai_predict": total_ai_predict,
        "dentist_diagnose": total_dentist_diagnose,
        "total_pic": total_total_pic
    })

    return output
