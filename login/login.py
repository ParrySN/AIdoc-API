from flask import jsonify
from db import connect_to_mysql, connect_to_oralcancer
import pymysql

def verify_user_from_aidoc(key):
    """Fetch user details from the aidoc_development database."""
    connection = connect_to_mysql()
    try:
        with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT national_id, username, is_patient, is_osm, is_specialist, is_admin "
                "FROM user WHERE national_id = %s OR username = %s", (key, key)
            )
            user = cursor.fetchone()
            if user:
                check_role(user)
                if user['national_id'] == key:
                    return {
                        "thaid": user['national_id'],
                        "roles": user['role'].split(',')
                    }, 200
                elif user['username'] == key:
                    return {
                        "username": user['username'],
                        "roles": user['role'].split(',')
                    }, 200
    except Exception as e:
        return {"message": str(e)}, 500
    finally:
        connection.close()
    return None, 401


def verify_user_from_questionnaire(key):
    """Fetch user details from the oralcancer database."""
    connection = connect_to_mysql()
    try:
        with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            # does not have work and dob 
            cursor.execute(
                """SELECT cid, name, sex, changwat, ampur, tumbon,address , phone
                FROM oralcancer.questionnaire WHERE cid = %s""", (key,)
            )
            patient = cursor.fetchone()
            if patient:
                first_name, last_name = split_name(patient['name'])

                phone = str(patient.get('phone', ''))
                if phone.startswith('0'):
                    phone = None
                else:
                    phone = '0' + phone

                if patient['cid'] == patient['name']:
                    return {
                        "thaid": patient['cid'],
                        "first_name": None,
                        "last_name": None,
                        "gender": patient['sex'],
                        "dob": None,
                        "province": patient['changwat'],
                        "district": patient['ampur'],
                        "subdistrict": patient['tumbon'],
                        "address": patient['address'],
                        "mobile": phone,
                        "career": None
                    }, 201

                return {
                    "thaid": patient['cid'],
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": patient['sex'],
                    "dob": None,
                    "province": patient['changwat'],
                    "district": patient['ampur'],
                    "subdistrict": patient['tumbon'],
                    "address": patient['address'],
                    "mobile": phone,
                    "career": None
                }, 201
            
    except Exception as e:
        return {"message": str(e)}, 500
    finally:
        connection.close()
    return {"message": "User not found"}, 401


def split_name(name):
    """Split the name into first and last names."""
    full_name = name.split(' ', 1) if name else ['']
    first_name = full_name[0].strip().rstrip('.')
    last_name = full_name[1].strip() if len(full_name) > 1 else ''  # Remove spaces
    return first_name, last_name

def check_role(user):
    """Assign roles to a user based on flags."""
    roles = []
    if user.get('is_patient'):
        roles.append('patient')
    if user.get('is_osm'):
        roles.append('osm')
    if user.get('is_specialist'):
        roles.append('specialist')
    if user.get('is_admin'):
        roles.append('admin')
    user['role'] = ','.join(roles)