import json
import db
from flask import jsonify, make_response, request
from decimal import Decimal

from submission import post_submission
from submission.get_submission_record_by_role import get_submission_record

def generate_record(data,imageList):
    # output = post_submission_record.init_record(data,imageList)
    output = {}
    return output

def generate_submission_record(data):
    output = get_submission_record(data)
    return output