import db
import json
from decimal import Decimal

#WIP to be done
def get_users_account_list(province):
    # Establish database connection
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            if not province:
                query_specialist_all = """
                    SELECT job_position,COUNT(*) as N 
                    FROM USER 
                    WHERE is_specialist = 1 
                    GROUP BY job_position
                """
                cursor.execute(query_specialist_all)
                specialist_all_query = cursor.fetchall()

                query_specialist_send = """
                    SELECT u.job_position, COUNT(DISTINCT u.id) AS N
                    FROM submission_record sr
                    LEFT JOIN user u
                    ON sr.sender_id = u.id
                    WHERE u.is_specialist = 1
                    GROUP BY u.job_position;
                """
                cursor.execute(query_specialist_send)
                specialist_send_query = cursor.fetchall()
                output = {
                    "all": specialist_all_query,
                    "send": specialist_send_query
                }
                all = []
                for i in specialist_all_query:
                    all.append({
                        "job": i[0],
                        "amount": i[1]
                    })
                print(output)
            else: 
                # query_ai = """
                # """
                # cursor.execute(query_ai, (province,province,))
                # ai_predict_query = cursor.fetchall()
                output = {}
            # Format Output
            output = []
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
