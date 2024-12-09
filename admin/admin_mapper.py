import common.common_mapper as cm
import common.date_util as du

def map_user_list_data(data):
    user_list = []

    for row in data:
        user = {
            "id": row[0],
            "name": row[1],
            "surname": row[2],
            "email": row[8] if row[8] else "None",
            "province": row[9],
            "job_position": cm.map_job_position_to_th(row[3]),
            "role": [],
            "total_submit": row[10]
        }

        if row[4] == 1:
            user["role"].append("patient")
        if row[5] == 1:
            user["role"].append("osm")
        if row[6] == 1:
            user["role"].append("specialist")
        if row[7] == 1:
            user["role"].append("admin")
        
        user_list.append(user)

    return user_list

def map_image_manage_list_data(data):
    image_manage_list = []
    for row in data:
        image= {
            "submission_id": row[0],
            "file_name": row[1],
            "submission_date": du.format_date_to_ddMMyyyy_time(row[2]),
            "ai_prediction": cm.map_ai_prediction_int(row[3]).upper(),
            "sender_fullname": f"{row[4]} {row[5]}",
            "sender_name": row[4],
            "sender_surname": row[5],
            "is_special_req": row[6],
            "province": row[7],
            "dentist_fullname": f"{row[11]} {row[12]}",
            "dentist_name": row[11],
            "dentist_surname": row[12],
            "dentist_comment": row[9],
            "national_id": row[10],
            "sender_job": cm.map_job_position_to_th(row[13]),
            "sender_id": row[14]
        }

        image_manage_list.append(image)

    return image_manage_list

