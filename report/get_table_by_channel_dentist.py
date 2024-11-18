import db
import json

def get_table():
    connection = db.connect_to_mysql()
    results = [] # Initialize an empty list to store results
    if connection:
        print("Connected to the database!")
        try:
            with connection.cursor() as cursor:  # Use a with block for automatic cursor closing
                query = """
                SELECT channel, dentist_feedback_code , COUNT(*) as N 
                FROM submission_record sr 
                GROUP By channel ="PATIENT", dentist_feedback_code 
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                for row in rows:
                    results.append(dict(zip(column_names, row))) #converting to json
                                
            output = {}
            diagnosis_code = {
                "OSCC": "OSCC",
                "OPMD": "OPMD",
                "Normal": "Normal",
                None: "Not graded"
            }

            for item in results:
                channel = "Patient" if item['channel'] == "PATIENT" else "Doctor"
                match item['dentist_feedback_code'] :
                    case "OSCC":
                        prediction = "OSCC"
                    case "OPMD":
                        prediction = "OPMD"
                    case "NORMAL":
                        prediction = "Normal"
                    case "AGREE":
                        prediction = "AGREE"
                    case None:
                        prediction = "Not graded"
                    case _:
                        prediction = 'else'
                count = item['N']

                if channel not in output:
                    output[channel] = {}
                    output[channel]['total'] = 0
                    
                try:
                    output[channel][prediction] = output[channel][prediction]+count
                except:
                    output[channel][prediction] = count
        
                if 'Total' not in output:
                    output['Total'] = {}
                    output['Total']['total'] =0     
                    
                try:
                    output['Total'][prediction] = output['Total'][prediction] + count
                    
                except:
                    output['Total'][prediction] = count
                
                output[channel]['total'] += count       
                output['Total']['total'] += count     
                
        except Exception as e:
                print(f"Error executing query: {e}")
                
    else:
        print("Failed to connect to the database.")
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    if connection:
        connection.close()
        print("MySQL connection closed.")
        
    return output