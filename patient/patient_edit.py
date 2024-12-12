from flask import json
import db

def get_user_info(user_id):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT name, surname, job_position, province, email, phone
                FROM user
                WHERE id = %s
            """
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()

            if not user:
                return json.dumps({"error": "No user found with the provided ID."}), 404

            return json.dumps({
                    "user_info": {
                        "name": user[0],
                        "surname": user[1],
                        "job_position": user[2],
                        "province": user[3],
                        "email": user[4],
                        "phone": user[5]
                    }
                }), 200

    except Exception as e:
        return json.dumps({"error": f"An error occurred while retrieving user info: {str(e)}"}), 500

    finally:
        connection.close()


def update_user_info(user_id, fields):
    connection = db.connect_to_mysql()
    if not connection:
        return json.dumps({"error": "Failed to connect to the database."}), 500

    try:
        with connection.cursor() as cursor:
                
            # check for changes
            cursor.execute("SELECT name, surname, job_position, province, email, phone FROM user WHERE id = %s", (user_id,))
            current_user = cursor.fetchone()
            
            if not current_user:
                return json.dumps({"error": "User not found"}), 404

            changes = {}
            for index, (db_field, new_value) in enumerate(fields):
                if current_user[index] != new_value:
                    changes[db_field] = new_value

            if not changes:
                return json.dumps({
                    "message": "No changes",
                    "user_info": current_user
                }), 200
            
            # update database
            update_fields = ', '.join(f"{field} = %s" for field in changes.keys())
            sql = f"UPDATE user SET {update_fields} WHERE id = %s"
            params = list(changes.values()) + [user_id]

            cursor.execute(sql, params)
            connection.commit()

            return json.dumps({
                    "message": "User info updated successfully",
                    "updated_field": changes,
                }), 200

    except Exception as e:
        return json.dumps({"error": f"An error occurred while updating user info: {str(e)}"}), 500

    finally:
        connection.close()

