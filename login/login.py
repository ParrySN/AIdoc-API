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


def verify_user_from_oralcancer(key):
    """Fetch user details from the oralcancer database."""
    connection = connect_to_oralcancer()
    try:
        with connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            # Query patients table
            cursor.execute(
                """SELECT license, fullname, sex, birth_date, province, address, phone, work
                FROM patients WHERE license = %s""", (key,)
            )
            patient = cursor.fetchone()
            if patient:
                full_name = patient['fullname'].split(' ', 1)
                return {
                    "thaid": patient['license'],
                    "first_name": full_name[0],
                    "last_name": full_name[1] if len(full_name) > 1 else '',
                    "gender": patient['sex'],
                    "dob": patient['birth_date'],
                    "province": patient['province'],
                    "address": patient['address'],
                    "phone": patient['phone'],
                    "job": patient['work']
                }, 201

            # Query users table
            cursor.execute(
                """SELECT license, name, surname, username, province, phone, work, role, email, hospital 
                FROM users WHERE username = %s""", (key,)
            )
            user = cursor.fetchone()
            if user:
                if user['username'] and user['username'].isdigit() and len(user['username']) == 13:
                    return {
                        "license": user['license'],
                        "first_name": user['name'],
                        "last_name": user['surname'],
                        "thaid": user['username'],
                        "province": user['province'],
                        "mobile": user['phone'],
                        "job": user['work'],
                        "role": user['role'],
                        "email": user['email'],
                        "hospital": user['hospital'],
                        "gender": None,
                        "district": None,
                        "subdistrict": None,
                        "address1": None,
                        "dob": None,
                    }, 201
                else:
                    return {
                        "license": user['license'],
                        "first_name": user['name'],
                        "last_name": user['surname'],
                        "username": user['username'],
                        "province": user['province'],
                        "mobile": user['phone'],
                        "career": user['work'],
                        "role": user['role'],
                        "email": user['email'],
                        "hospital": user['hospital'],
                        "gender": None,
                        "district": None,
                        "subdistrict": None,
                        "address1": None,
                        "thaid": None,
                        "dob": None,
                    }, 201
    except Exception as e:
        return {"message": str(e)}, 500
    finally:
        connection.close()
    return {"message": "user not found"}, 401


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