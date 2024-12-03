import json
import db


def delete_user():
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            delete_submission_query = "DELETE FROM submission_record WHERE sender_id = %s"
            cursor.execute(delete_submission_query, (id,))

            connection.commit()
            sql = "DELETE FROM user WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()

            if cursor.rowcount == 0:
                return json.dumps({"error": "User not found."}), 404

    except Exception as e:
        return json.dumps({"error": f"An error occurred while deleting user: {e}"}), 500
    
    finally:
        connection.close()

    return json.dumps({"message": f"User with ID {id} deleted successfully."}), 200