import datetime
import os
from flask import json, jsonify, flash
from werkzeug.utils import secure_filename
import db

def init_record(data,imageList):
    output = {}
    # session['sender_mode'] = role //check role
    submission = data['is_submit']
    if request.method == 'POST':
        if data['is_rotate']=='true': # Rotate the image
            imageName = data['fname']
            rotate_temp_image(imageName)
            output = {'uploadedImage': imageName}
        elif submission=='false': # Load and show the image, wait for the confirmation
            imageNameList = []
            for imageFile in imageList: 
                if imageFile and allowed_file(imageFile.filename):
                    fileName, fileExtension = os.path.splitext(imageFile.filename)
                    fileName = secure_filename(fileName)
                    if fileName != '':
                        imageName = fileName+fileExtension
                    else:
                        newFileName = 'secured_filename'
                        suffix = datetime.now().strftime("%y%m%d_%H%M%S")
                        imageName = "_".join([newFileName, suffix]) + fileExtension 
                    imagePath = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp', imageName)
                    imageFile.save(imagePath)
                    #Create the temp thumbnail
                    pil_img = Image.open(imagePath).convert('RGB')

                    # Check image quality
                    global qualityChecker
                    qualityResults = qualityChecker.predict(pil_img)
                    print(qualityResults['Class_Name'])
                    if qualityResults['Class_ID'] == 0:
                        flash(f'ระบบตรวจสอบพบว่าไฟล์ {imageName} คุณภาพของรูปไม่ได้มาตรฐาน ภาพช่องปากอาจไม่ชัด (เบลอ) หรือมืดเกินไป (เปิดไฟส่องสว่างช่องปากด้วย) กรุณานำส่งรูปที่ได้คุณภาพเท่านั้น')
                    elif qualityResults['Class_ID'] == 1:
                        flash(f'ระบบตรวจสอบพบว่าไฟล์ {imageName} ไม่ปรากฎช่องปากในภาพ กรุณานำส่งภาพถ่ายที่ได้มุมมองมาตรฐานตามตัวอย่างเท่านั้น')
                    output['imageQuality'] = qualityResults['Class_ID']

                    pil_img = create_thumbnail(pil_img)
                    pil_img.save(os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp', 'thumb_' + imageName)) 
                    # Save the current filenames on session for the upcoming prediction
                    imageNameList.append(imageName)
                else:
                    flash(f'ไฟล์ {imageName} ไม่ใช่ชนิดรูปภาพที่กำหนด ระบบรับข้อมูลเฉพาะที่เป็นชนิดรูปภาพที่กำหนดเท่านั้น')
            if len(imageList)>0:
                # Save the current filenames on session for the upcoming prediction
                session['imageNameList'] = imageNameList
            else:
                session.pop('imageNameList', None)
            if imageName:
                output['uploadedImage'] = imageName # Send back path of the last submitted image (if sent for more than 1)
            if g.user['default_location']:
                location = ast.literal_eval(g.user['default_location'])
                if location['district']:
                    output['default_location_text'] = "สถานที่คัดกรอง: ตำบล"+location['district']+" อำเภอ"+location['amphoe']+" จังหวัด"+location['province']+" " +str(location['zipcode'])
                else:
                    output['default_location_text'] = "สถานที่คัดกรอง: จังหวัด"+location['province']    
            else:
                location = {'district': None,
                            'amphoe': None,
                            'province': g.user['province'],
                            'zipcode': None}
                output['default_location_text'] = "สถานที่คัดกรอง: จังหวัด"+location['province']
            output['earthchieAPI'] = True # enable Earthchie's Thailand Address Auto-complete API
        elif submission=='true': # upload confirmation is submitted
            # Check if submission list is in the queue (session), if so submit them to the Submission Module and the AI Prediction Engine
            if 'imageNameList' in session and session['imageNameList']:
                if role=='patient':
                    if request.form.get('inputPhone') is not None and request.form.get('inputPhone')!='':
                        session['sender_phone'] = request.form.get('inputPhone')
                    else:
                        session['sender_phone'] = None
                    if request.form.get('sender_id') is not None and request.form.get('sender_id')!='':
                        session['sender_id'] = request.form.get('sender_id')
                    elif session['sender_phone'] is None:
                        session['sender_id'] = session['user_id']
                    else:
                        session['sender_id'] = None
                if role=='osm':
                    if request.form.get('inputIdentityID') is not None and request.form.get('inputIdentityID')!='':
                        session['patient_national_id'] = request.form.get('inputIdentityID')
                    else:
                        session['patient_national_id'] = None
                    if request.form.get('patient_id')!='':
                        session['patient_id'] = request.form.get('patient_id')
                    else:
                        session['patient_id'] = None
                if request.form.get('location') is not None and request.form.get('location')!='':
                    session['location'] = ast.literal_eval(request.form.get('location'))
                else:
                    session['location'] = {'district': None,
                                           'amphoe': None,
                                           'province': g.user['province'],
                                           'zipcode': None}
                
                upload_submission_module(target_user_id=session['user_id'])

                lastImageName = list(session['imageNameList'])[-1]
                db, cursor = get_db()
                sql = "SELECT id FROM submission_record WHERE fname=%s"
                val = (lastImageName, )
                cursor.execute(sql, val)
                result = cursor.fetchall() # There might be several images of the same name (duplication is checked only the same user upload the same files)
                result = result[-1] # The last image will be selected
                #Clear submission queue in the session
                session.pop('imageNameList', None)
                if role=='patient':
                    session.pop('sender_phone', None)
                    session.pop('sender_id', None)
                    session.pop('location', None)
                elif role=='osm':
                    session.pop('patient_national_id', None)
                    session.pop('patient_id', None)
                    session.pop('location', None)
                return redirect(url_for('image.diagnosis', role=role, img_id=result['id']))
    return output

# region rotate_temp_image
def rotate_temp_image(imagename):
    imagePath = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp', imagename)
    pil_img = Image.open(imagePath) 
    pil_img = pil_img.rotate(-90, expand=True)
    pil_img.save(imagePath)

    # Create the thumbnails
    pil_img = create_thumbnail(pil_img)
    pil_img.save(os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp', 'thumb_' + imagename))

 # region allowed_files
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS