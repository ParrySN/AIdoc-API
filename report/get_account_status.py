import db
import json
from decimal import Decimal

def get_account_status():
    # Establish database connection
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            query_ai = """
            SELECT ai_prediction, COUNT(*) as N 
            FROM submission_record 
            GROUP BY ai_prediction
            """
            cursor.execute(query_ai)
            ai_predict_query = cursor.fetchall()
            total_pic = sum(value for key, value in ai_predict_query)
            ai_predict = mapAiPrediction(ai_predict_query)
            # Format Output
            output = {}
            output['total_pic'] = total_pic
            output['ai_predict'] = ai_predict
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
