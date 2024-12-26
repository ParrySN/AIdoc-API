from authentication.update_token import generate_additional_claims, update_access_token
from flask import jsonify
from flask_jwt_extended import create_access_token, decode_token
from common.common_mapper import map_role_to_list
import db
import pymysql

def verify_user_from_aidoc(key):
    connection,cursor = db.get_db()
    try:
        with cursor:
            query ="""
            SELECT 
                *
                FROM user 
                WHERE national_id = %s 
                OR username = %s
            """
            cursor.execute(query, (key, key))
            user = cursor.fetchone()
            if user:
                role = map_role_to_list(user)
                if user['username'] == key:
                    return {
                        "channel": "DENTIST",
                        "username": user['username'],
                        "roles": role
                    }, 200
                elif user['national_id'] == key:
                    if user['is_patient'] == 1 and user['is_osm'] == 0 and user['is_specialist'] == 0 and user['is_admin'] == 0:
                        channel = "PATIENT"
                        additional_claims = generate_additional_claims(channel,role,user)
                        access_token = create_access_token(identity=str(role), additional_claims=additional_claims)
                        update_access_token(user['id'], access_token, False)
                        return {
                            "channel": channel,
                            "thaid": user['national_id'],
                            "roles": role,
                            "access_token": access_token
                        }, 200
                    else:
                        return {
                            "channel": "OSM",
                            "thaid": user['national_id'],
                            "roles": role
                        }, 200 
    except Exception as e:
        return {"message": str(e)}, 500

    return None, 401


def verify_user_from_questionnaire(key):
    connection,cursor = db.get_db_2()
    try:
        with cursor:
            query ="""
                SELECT 
                cid, 
                name, 
                sex, 
                changwat, 
                ampur, 
                tumbon,
                address , 
                phone
                FROM oralcancer.questionnaire 
                WHERE cid = %s"""
            cursor.execute(query, (key,))
            patient = cursor.fetchone()
            if patient:
                first_name, last_name = split_name(patient['name'])

                phone = str(patient.get('phone', ''))
                if not phone.startswith('0'):
                    phone = '0' + phone

                if patient['cid'] == patient['name']:
                    first_name, last_name = None, None

                return {
                    "thaid": patient['cid'],
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": patient['sex'],
                    "province": patient['changwat'],
                    "district": patient['ampur'],
                    "subdistrict": patient['tumbon'],
                    "address": patient['address'],
                    "mobile": phone,
                }, 201
            
    except Exception as e:
        return {"message": str(e)}, 500

    return {"message": "User not found"}, 401


def split_name(name):
    full_name = name.split(' ', 1) if name else ['']
    first_name = full_name[0].strip().rstrip('.')
    last_name = full_name[1].strip() if len(full_name) > 1 else '' 
    return first_name, last_name

    