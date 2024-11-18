import json
import db
from report import get_table_by_channel_ai
from report import get_table_by_channel_dentist

def report():

    dentist = get_table_by_channel_dentist.get_table()
    ai = get_table_by_channel_ai.get_table()
    output = {}
    output['ai'] = ai
    output['dentist'] = dentist
    return json.dumps(output, indent=2)











