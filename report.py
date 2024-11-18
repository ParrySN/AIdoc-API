import pymysql
import json

def categorize_score(score_string):
    try:
        scores = [float(x) for x in score_string.split()]
        max_score_index = scores.index(max(scores))

        if max_score_index == 0:
            return "NM"  # "Normal" maps to 1
        elif max_score_index == 1:
            return "OPMD"  # "OSCC" maps to 2
        elif max_score_index == 2:
            return "OSCC"  # "OPMD" maps to 3
        else:
            return -1 # Handle cases where the index is out of range (optional)

    except (ValueError, IndexError):  # Handle potential errors during conversion or empty strings
        return -1

connection = pymysql.connect(
        host='icohold.anamai.moph.go.th', # database server
        port=3306,
        database='oralcancer',	
        user='patiwet', 	# mysql username
        password='icoh2017p@ssw0rd' 	# mysql password for the username
    )
output = {
    "Total":{
        "ai":{
            "OSCC": 0,
            "OPMD": 0,
            "NM": 0
        },
        "dentist":{
            "OSCC": 0,
            "OPMD": 0,
            "NM": 0
        }
    }
}
positive = 0
total = 0
if connection:
    print("Connected to the database!")
    try:
        with connection.cursor() as cursor:  # Use a with block for automatic cursor closing
            table = ['users','patients']
            for t in table:
                results = [] # Initialize an empty list to store results    
                query = """
                select ph.userid, p.work, ph.score, ph.dentist_comment 
                from patients_history ph left join """ + t + """ p on ph.userid = p.id
                where work is not NULL
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                ai = {
                    "OSCC": 0,
                    "OPMD": 0,
                    "NM": 0
                }
                dentist = {
                    "OSCC": 0,
                    'NM': 0,
                    "OPMD": 0
                }
                for row in rows:
                    row_dict = dict(zip(column_names, row))
                    row_dict['score'] = categorize_score(row_dict['score']) #categorize score to 1,2,3
                    ai[row_dict['score']] += 1
                    try :
                        dentist[row_dict['dentist_comment']] += 1
                        total += 1
                    except:
                        continue
                    
                    if row_dict['score'] == row_dict['dentist_comment']:
                        positive += 1
                    elif row_dict['dentist_comment'] in ["เห็นด้วย~ยืนยันว่าไม่พบรอยโรคจริง","เห็นด้วย~ยืนยันว่าไม่พบรอยโรคจริง กรุณาส่งภาพถ่ายช่องปากมุมมองอื่น ๆ มาให้ตรวจด้วย เช่น ข้างลิ้น กระพุ้งแก้มเป็นต้น" ]:
                        positive += 1
                        total += 1
                        
                output[t] = {'ai':ai, 'dentist':dentist}
    except Exception as e:
        print(f"Error executing query: {e}")
else:
    print("Failed to connect to the database.")

output["Total"]['ai']["OSCC"]  = output["users"]['ai']["OSCC"] + output["patients"]['ai']["OSCC"]
output["Total"]['ai']["OPMD"]  = output["users"]['ai']["OPMD"] + output["patients"]['ai']["OPMD"]
output["Total"]['ai']["NM"]  = output["users"]['ai']["NM"] + output["patients"]['ai']["NM"]
output["Total"]['dentist']["OSCC"]  = output["users"]['dentist']["OSCC"] + output["patients"]['dentist']["OSCC"]
output["Total"]['dentist']["OPMD"]  = output["users"]['dentist']["OPMD"] + output["patients"]['dentist']["OPMD"]
output["Total"]['dentist']["NM"]  = output["users"]['dentist']["NM"] + output["patients"]['dentist']["NM"]
output['accuracy'] = positive/total * 100


if connection:
    connection.close()
    print("MySQL connection closed.")
    print(json.dumps(output, indent=2))
