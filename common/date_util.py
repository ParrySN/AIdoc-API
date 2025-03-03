from datetime import datetime
from dateutil.parser import parse
from datetime import date

def format_date_to_ddMMyyyy_time(date):
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    
    return date.strftime("%d/%m/%Y %H:%M")

def calculate_age(born):
    if isinstance(born,str):
        born = parse(born)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))