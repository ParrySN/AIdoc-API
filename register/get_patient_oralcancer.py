import db
from flask import json

def get_data_oralcancer(id):
    connection, cursor = db.get_db2()
    try:
        with cursor:
            patient_data = fetch_data_by_nationalId(cursor,id)
            
            output = {
                "message":"get successfully",
                "patient_info": patient_data,
            }
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred","details":str(e)}),500
    finally:
        db.close_db()

    return output

def fetch_data_by_nationalId(cursor,id):
    sql = """
    SELECT
        p.fullname,
        p.work,
        p.sex,
        p.license,
        p.address,
        p.province,
        p.email,
        p.phone,
        p.birth_date
    FROM
        patients p
    WHERE
		p.license like %s;
    """

    cursor.execute(sql,(id,))
    user_from_oralcancer = cursor.fetchall()
    return user_from_oralcancer