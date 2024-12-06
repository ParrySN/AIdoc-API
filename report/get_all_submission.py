import db
import json
from decimal import Decimal
from common import common_mapper as cm

def get_all_submission(province):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500

    try:
        with connection.cursor() as cursor:
            ai_predict_query, total_pic = fetch_ai_predictions(cursor, province)
            
            ai_predict = cm.map_ai_prediction(ai_predict_query)
            
            if not ai_predict:
                ai_predict = {"normal": 0, "opmd": 0, "oscc": 0}
                total_pic = 0
            
            output = {
                'total_pic': total_pic,
                'ai_predict': ai_predict
            }

    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            "ai_predict": {"normal": 0, "opmd": 0, "oscc": 0},
            "total_pic": 0
        }
    
    finally:
        connection.close()
        
    return output

def fetch_ai_predictions(cursor, province):
    if province:
        query = """
        SELECT ai_prediction, COUNT(*) as N 
        FROM submission_record 
        WHERE location_province = %s
        GROUP BY ai_prediction
        """
        cursor.execute(query, (province,))
    else:
        query = """
        SELECT ai_prediction, COUNT(*) as N 
        FROM submission_record 
        GROUP BY ai_prediction
        """
        cursor.execute(query)

    ai_predict_query = cursor.fetchall()

    total_pic = sum(value for _, value in ai_predict_query)

    return ai_predict_query, total_pic

