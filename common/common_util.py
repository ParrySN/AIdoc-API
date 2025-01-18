import re

from flask import json, jsonify
def validate_license(license):
    license_pattern = r'^[0-9]*$'
    license_validation_flag = re.match(license_pattern, license) is not None
    if not license_validation_flag:
        error_msg = "กรุณาเลขที่ใบอนุญาตให้ถูกต้อง กรอกเฉพาะตัวเลข ไม่ต้องใส่ ท. หรือ พ."
        return False, error_msg
    return True, None

def validate_national_id(national_id):
    # National ID Checksum
    # Define national id pattern
    digit13_pattern = r'^\d{13}$'
    # Convert the ID string to a list of integers
    digits = [int(digit) for digit in national_id]
    last_digit = digits[-1]
    # Calculate the weighted sum using list comprehension
    weighted_sum = sum(digit * (13 - i) for i, digit in enumerate(digits[:-1]))
    check_digit = (11- (weighted_sum%11))%10
    check_sum = (check_digit == last_digit)
    national_id_checksum_flag = (re.match(digit13_pattern, national_id) is not None) and check_sum
    if not national_id_checksum_flag:
        error_msg = "กรุณากรอกรหัสบัตรประชาชนให้ถูกต้อง"
        return False, error_msg
    return True, None

def confirm_input(input_value, confirm_value, field_name):
    # Validate inputs
    if not isinstance(input_value, str) or not isinstance(confirm_value, str):
        error_msg = "Invalid input: both values must be strings."
        return json.dumps({"error": error_msg}), 400
    
    if input_value != confirm_value:
        error_msg = f"กรุณากรอก {field_name} ให้ตรงกันทั้งสองครั้ง" 
        return False, error_msg
    return True, None


def validate_phone(phone):
    phone_pattern = r'^\d{9,10}$'
    phone_validation_flag = re.match(phone_pattern, phone) is not None
    if not phone_validation_flag:
        error_msg = "กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้อง"
        return False, error_msg
    return True, None

import re

def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    email_validation_flag = re.match(email_pattern, email) is not None
    if not email_validation_flag:
        error_msg = "กรุณากรอกอีเมลให้ถูกต้อง"
        return False, error_msg
    return True, None
