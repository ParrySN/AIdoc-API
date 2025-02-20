from datetime import datetime
import db

def format_date_to_ddMMyyyy_time(date):
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    
    return date.strftime("%d/%m/%Y %H:%M")


def check_date(cursor,start_date,end_date):
    if start_date is None or end_date is None:
        if start_date is None:
            cursor.execute("SELECT MIN(created_at) AS min_date FROM submission_record WHERE channel = 'DENTIST'")
            result = cursor.fetchone()
            start_date = result['min_date']
        if end_date is None:
            cursor.execute("SELECT NOW() AS end_date")
            result = cursor.fetchone()
            end_date = result['end_date']
    return start_date,end_date
