import json
import db
from flask import jsonify, make_response, request
from decimal import Decimal

from submission import post_submission_record

def generate_record(data,imageList):
    # output = post_submission_record.init_record(data,imageList)
    output = {}
    return output