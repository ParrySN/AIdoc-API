import db
import json
from decimal import Decimal

def get_image_manage_list():
    # Establish database connection
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
         output = {}
    except Exception as e:
        output = json.dumps({"error": f"An error occurred while fetching user accounts: {e}"})
        return output
    
    finally:
        # Close Connection
        connection.close()
    # Create a response object
    response = {}
    return response

