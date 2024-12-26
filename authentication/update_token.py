import db
from flask_jwt_extended import get_jwt, decode_token

def update_access_token(user_id, access_token, is_revoke):
    connection, cursor = db.get_db()
    try:
        with cursor:
            decoded_token = decode_token(access_token)
            jti = decoded_token.get("jti")
            query = """
            INSERT INTO access_token (user_id, jti, is_revoke, create_at, update_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE 
                jti = VALUES(jti),
                is_revoke = VALUES(is_revoke),
                update_at = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (user_id, jti, is_revoke))
        return {"message": "Access token updated successfully"}, 200
    except Exception as e:
        return {"message": str(e)}, 500
    
def generate_additional_claims(channel,role,user):
    additional_claims = {
        'channel': channel,
        'role': role,
        **user 
    }
    return additional_claims