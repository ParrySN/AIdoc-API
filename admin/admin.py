import json
from admin import get_user_account_list, get_user_edit_info, update_user_info
import db
from flask import jsonify, make_response, request
from decimal import Decimal

def getAdminPage():
    output = get_user_account_list.get_users()
    return jsonify(output)

def deleteUser(id):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM user WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()

            if cursor.rowcount == 0:
                # No rows affected, so user with that id doesn't exist
                return json.dumps({"error": "User not found."}), 404

    except Exception as e:
        output = json.dumps({"error": f"An error occurred while deleting user: {e}"})
        return output, 500
    
    finally:
        connection.close()

    return json.dumps({"message": f"User with ID {id} deleted successfully."}), 200

def getUserEditInfo(id):
    output = get_user_edit_info.getUserEditProfile(id)
    return output

def updateUserInfo(data):
    output = update_user_info.updateUserInfo(data)
    return output
    













