import json
import db

def get_table():
    connection = db.connect_to_mysql()
    results = [] # Initialize an empty list to store results
    if connection:
        print("Connected to the database!")
        try:
            with connection.cursor() as cursor:  # Use a with block for automatic cursor closing
                query = """
                SELECT channel, ai_prediction, COUNT(*) as N 
                FROM submission_record
                GROUP By channel, ai_prediction
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                for row in rows:
                    results.append(dict(zip(column_names, row))) #converting to json            
            output = {}
            prediction_mapping = {  # Create a dictionary for the mappings
                0: "Normal",
                1: "OPMD",
                2: "OSCC"
            }

            for item in results:
                channel = "Patient" if item['channel'] == "PATIENT" else "Doctor"
                prediction = prediction_mapping.get(item['ai_prediction'], str(item['ai_prediction'])) # Get mapped value or keep original if not found
                count = item['N']

                if channel not in output:
                    output[channel] = {}
                try:
                    output[channel][prediction] = output[channel][prediction]+count
                except:
                    output[channel][prediction] = count
                
                if 'Total' not in output:
                    output['Total'] = {}
                try:
                    output['Total'][prediction] = output['Total'][prediction]+count
                except:
                    output['Total'][prediction] = count
                    

        except Exception as e:
            print(f"Error executing query: {e}")
            return json.dumps({"error": str(e)}), 500  # Return 500 for internal server error
            
    else:
        print("Failed to connect to the database.")
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    if connection:
        connection.close()
        print("MySQL connection closed.")
        
    return output

