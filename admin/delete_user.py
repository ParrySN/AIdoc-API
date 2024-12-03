import json
import db


def delete_user():
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500
    
    try:
        with connection.cursor() as cursor:
            sql_delete_submission = "DELETE FROM submission_record WHERE sender_id = %s"
            cursor.execute(sql_delete_submission, (id,))
            connection.commit()
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