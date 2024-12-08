import json
import db


def delete_user(id):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            delete_submission_record(cursor, id)
            connection.commit()

            update_submission_record(cursor, id)
            connection.commit()

            delete_user_query(cursor, id)
            connection.commit()

            if cursor.rowcount == 0:
                return json.dumps({"error": "User not found."}), 404

    except Exception as e:
        return json.dumps({"error": f"An error occurred while deleting user: {e}"}), 500
    
    finally:
        connection.close()

    return json.dumps({"message": f"User with ID {id} deleted successfully."}), 200

def delete_submission_record(cursor, id):
    query = "DELETE FROM submission_record WHERE sender_id = %s"
    cursor.execute(query, (id,))

def update_submission_record(cursor, id):
    query = "UPDATE submission_record SET patient_id = NULL WHERE patient_id = %s"
    cursor.execute(query, (id,))

def delete_user_query(cursor, id):
    query = "DELETE FROM user WHERE id = %s"
    cursor.execute(query, (id,))
