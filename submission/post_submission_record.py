import datetime
import os
from flask import json, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image, ImageFilter
import db
import ast
import cv2
import numpy as np
import tensorflow as tf
import common.image_quality_checker as image_quality_checker

qualityChecker = image_quality_checker.image_quality_checker()

def init_record(data,imageList):
    output = {}
    session['sender_mode'] = role
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
                        return  json.dumps({"error": f'ระบบตรวจสอบพบว่าไฟล์ {imageName} คุณภาพของรูปไม่ได้มาตรฐาน ภาพช่องปากอาจไม่ชัด (เบลอ) หรือมืดเกินไป (เปิดไฟส่องสว่างช่องปากด้วย) กรุณานำส่งรูปที่ได้คุณภาพเท่านั้น'}), 400
                    elif qualityResults['Class_ID'] == 1:
                        return  json.dumps({"error": f'ระบบตรวจสอบพบว่าไฟล์ {imageName} ไม่ปรากฎช่องปากในภาพ กรุณานำส่งภาพถ่ายที่ได้มุมมองมาตรฐานตามตัวอย่างเท่านั้น'}), 400
                    output['imageQuality'] = qualityResults['Class_ID']

                    pil_img = create_thumbnail(pil_img)
                    pil_img.save(os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp', 'thumb_' + imageName)) 
                    # Save the current filenames on session for the upcoming prediction
                    imageNameList.append(imageName)
                else:
                    return  json.dumps({"error": f'ไฟล์ {imageName} ไม่ใช่ชนิดรูปภาพที่กำหนด ระบบรับข้อมูลเฉพาะที่เป็นชนิดรูปภาพที่กำหนดเท่านั้น'}), 400
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
    return render_template(role+"_upload.html", data=data)

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

# region create_thumbnail
def create_thumbnail(pil_img):
    MAX_SIZE = 342
    width = pil_img.size[0]
    height = pil_img.size[1]
    if height < MAX_SIZE:
        new_height = MAX_SIZE
        new_width  = int(new_height * width / height)
        pil_img = pil_img.resize((new_width, new_height), Image.NEAREST)
        if new_width > MAX_SIZE:
            canvas = Image.new(pil_img.mode, (new_width, new_width), (255, 255, 255))
            canvas.paste(pil_img)
            pil_img = canvas.resize((MAX_SIZE, MAX_SIZE), Image.NEAREST)
    else:
        pil_img.thumbnail((MAX_SIZE,MAX_SIZE))
    return pil_img

# Upload Submission Module
def upload_submission_module(target_user_id):
    if session['imageNameList']:
        # Define the related directories
        tempDir = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp')

        # Model prediction
        ai_predictions = []
        ai_scores = []
        for i, filename in enumerate(session['imageNameList']):
            imgPath = os.path.join(tempDir, filename)
            outlined_img, prediction, scores, mask = oral_lesion_prediction(imgPath)

            outlined_img.save(os.path.join(tempDir, 'outlined_'+filename))
            mask.save(os.path.join(tempDir, 'mask_'+filename))

            #Create the thumbnail and saved to temp folder
            pil_img = Image.open(os.path.join(tempDir, 'outlined_'+filename)) 
            pil_img = create_thumbnail(pil_img)
            pil_img.save(os.path.join(current_app.config['IMAGE_DATA_DIR'], 'temp', 'thumb_outlined_' + filename)) 

            ai_predictions.append(prediction)
            ai_scores.append(str(scores))
        
        if session['imageNameList']:
            session['ai_predictions'] = ai_predictions
            session['ai_infos'] = ai_scores
        else:
            session.pop('ai_predictions', None)
            session.pop('ai_infos', None)
        
        # Create directory for the user (using user_id) if not exist
        user_id = str(target_user_id)
        uploadDir = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'upload', user_id)
        thumbUploadDir = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'upload', 'thumbnail', user_id)
        outlinedDir = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'outlined', user_id)
        thumbOutlinedDir = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'outlined', 'thumbnail', user_id)
        maskDir = os.path.join(current_app.config['IMAGE_DATA_DIR'], 'mask', user_id)
        os.makedirs(uploadDir, exist_ok=True)
        os.makedirs(thumbUploadDir, exist_ok=True)
        os.makedirs(outlinedDir, exist_ok=True)
        os.makedirs(thumbOutlinedDir, exist_ok=True)
        os.makedirs(maskDir, exist_ok=True)

        # Copy files to the storage
        checked_filename_lst = []
        for filename in session['imageNameList']:
            if os.path.isfile(os.path.join(tempDir, filename)):

                checked_filename = rename_if_duplicated(uploadDir, filename)

                shutil.copy2(os.path.join(tempDir, filename), os.path.join(uploadDir, checked_filename))
                shutil.copy2(os.path.join(tempDir, 'thumb_'+filename), os.path.join(thumbUploadDir, checked_filename))
                shutil.copy2(os.path.join(tempDir, 'outlined_'+filename), os.path.join(outlinedDir, checked_filename))
                shutil.copy2(os.path.join(tempDir, 'thumb_outlined_'+filename), os.path.join(thumbOutlinedDir, checked_filename))
                shutil.copy2(os.path.join(tempDir, 'mask_'+filename), os.path.join(maskDir, checked_filename))

                checked_filename_lst.append(checked_filename)
        session['imageNameList'] = checked_filename_lst

        # Try to clear temp folder if #files are more than CLEAR_TEMP_THRESHOLD
        if len(os.listdir(tempDir)) > current_app.config['CLEAR_TEMP_THRESHOLD']:
            for filename in os.listdir(tempDir):
                if os.path.isfile(os.path.join(tempDir, filename)):
                    os.remove(os.path.join(tempDir, filename))

        # Add the prediction record to the database
        for i, filename in enumerate(session['imageNameList']):
            connection, cursor = db.get_db()
            
            if session['sender_mode']=='dentist':
                
                if g.user['default_location'] is None or str(g.user['default_location'])!=str(session['location']):
                    sql = "UPDATE user SET default_location=%s WHERE id=%s"
                    val = (str(session['location']), session['user_id'])
                    cursor.execute(sql, val)
                    load_logged_in_user()

                sql = '''INSERT INTO submission_record
                    (fname,
                    sender_id,
                    location_district,
                    location_amphoe,
                    location_province,
                    location_zipcode,
                    ai_prediction,
                    ai_scores,
                    channel)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                val = (filename,
                       session['user_id'],
                       session['location']['district'],
                       session['location']['amphoe'],
                       session['location']['province'],
                       session['location']['zipcode'],
                       ai_predictions[i],
                       ai_scores[i],
                       'DENTIST')
                cursor.execute(sql, val)


            elif session['sender_mode']=='patient':

                if g.user['default_location'] is None or str(g.user['default_location'])!=str(session['location']):
                    sql = "UPDATE user SET default_location=%s WHERE id=%s"
                    val = (str(session['location']), session['user_id'])
                    cursor.execute(sql, val)
                    load_logged_in_user()

                if 'sender_phone' in session and session['sender_phone']:
                    sql = "UPDATE user SET default_sender_phone=%s WHERE id=%s"
                    val = (session['sender_phone'], session['user_id'])
                    cursor.execute(sql, val)
                    load_logged_in_user()
                
                if (g.user['default_sender_phone'] and ('sender_phone' not in session or session['sender_phone'] is None)):
                    sql = "UPDATE user SET default_sender_phone=NULL WHERE id=%s"
                    val = (session['user_id'], )
                    cursor.execute(sql, val)
                    load_logged_in_user()
                
                sql = '''INSERT INTO submission_record 
                        (fname,
                        sender_id,
                        sender_phone,
                        location_district,
                        location_amphoe,
                        location_province,
                        location_zipcode,
                        patient_id,
                        ai_prediction,
                        ai_scores,
                        channel)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                val = (filename,
                        session['sender_id'],
                        session['sender_phone'],
                        session['location']['district'],
                        session['location']['amphoe'],
                        session['location']['province'],
                        session['location']['zipcode'],
                        session['user_id'],
                        ai_predictions[i],
                        ai_scores[i],
                        'PATIENT')
                cursor.execute(sql, val)
                
                cursor.execute("SELECT LAST_INSERT_ID()")
                row = cursor.fetchone()
                sql = "INSERT INTO patient_case_id (id) VALUES (%s)"
                val = (row['LAST_INSERT_ID()'],)
                cursor.execute(sql, val)

            elif session['sender_mode']=='osm':

                if g.user['default_location'] is None or str(g.user['default_location'])!=str(session['location']):
                    sql = "UPDATE user SET default_location=%s WHERE id=%s"
                    val = (str(session['location']), session['user_id'])
                    cursor.execute(sql, val)
                    load_logged_in_user()

                sql = '''INSERT INTO submission_record 
                        (fname, 
                        sender_id,
                        location_district,
                        location_amphoe,
                        location_province,
                        location_zipcode,
                        patient_id,
                        patient_national_id,
                        ai_prediction,
                        ai_scores,
                        channel)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                val = (filename,
                        session['user_id'],
                        session['location']['district'],
                        session['location']['amphoe'],
                        session['location']['province'],
                        session['location']['zipcode'],
                        session['patient_id'],
                        session['patient_national_id'],
                        ai_predictions[i],
                        ai_scores[i],
                        'OSM')
                cursor.execute(sql, val)

                cursor.execute("SELECT LAST_INSERT_ID()")
                row = cursor.fetchone()
                sql = "INSERT INTO patient_case_id (id) VALUES (%s)"
                val = (row['LAST_INSERT_ID()'],)
                cursor.execute(sql, val)


# AI Prediction Engine
def oral_lesion_prediction(imgPath):
    
    #import tensorflow as tf
    
    img = tf.keras.utils.load_img(imgPath, target_size=(342, 512, 3))
    img = tf.expand_dims(img, axis=0)

    global model
    pred_mask = model.predict(img)

    output_mask = tf.math.argmax(pred_mask, axis=-1)
    output_mask = output_mask[..., tf.newaxis]
    output_mask = output_mask[0]

    predictionMask = tf.math.not_equal(output_mask, 0)
    
    ### The Connected Component Analysis, requires OpenCV ##########
    analysis = cv2.connectedComponentsWithStats(predictionMask.numpy().astype(dtype='uint8'), 4, cv2.CV_32S)
    (numLabels, labels, stats, centroid) = analysis
    output = np.zeros((342, 512), dtype="uint8")
    maxArea = 0
    for i in range(1, numLabels):
        area = stats[i, cv2.CC_STAT_AREA]
        maxArea = max(maxArea, area)
        if area > 500: 
            componentMask = (labels == i).astype("uint8")*255
            output = cv2.bitwise_or(output, componentMask) 
    predictionMask = tf.convert_to_tensor(output)
    predictionMask = tf.math.equal(predictionMask, 255)
    predictionMask = predictionMask[..., tf.newaxis]
    ################################################################

    pred_mask = tf.squeeze(pred_mask, axis=0)  # Remove batch dimension
    backgroundChannel = pred_mask[:,:,0]
    opmdChannel = pred_mask[:,:,1]
    osccChannel = pred_mask[:,:,2]
    
    #predictionMaskSum = tf.reduce_sum(tf.cast(predictionMask,  tf.int64)) # Count number of pixels in prediction mask
    predictionIndexer = tf.squeeze(predictionMask, axis=-1) # Remove singleton dimension (last index)
    if maxArea>500: # Threshold to cut noises are 500 pixels
        opmdScore = tf.reduce_mean(opmdChannel[predictionIndexer])
        osccScore = tf.reduce_mean(osccChannel[predictionIndexer])
        backgroundScore = tf.reduce_mean(backgroundChannel[predictionIndexer])
        if opmdScore>osccScore:
            predictClass = 1
        else:
            predictClass = 2
    else:
        backgroundIndexer = tf.math.logical_not(predictionIndexer)
        opmdScore = tf.reduce_mean(opmdChannel[backgroundIndexer])
        osccScore = tf.reduce_mean(osccChannel[backgroundIndexer])
        backgroundScore = tf.reduce_mean(backgroundChannel[backgroundIndexer])
        predictClass = 0

    # Pillow is used to create the boundary
    # Pillow has a very strong relationship with tensorflow
    output = tf.keras.utils.array_to_img(predictionMask)
    edge_img = output.filter(ImageFilter.FIND_EDGES)
    dilation_img = edge_img.filter(ImageFilter.MaxFilter(3))

    full_img = Image.open(imgPath)
    full_dilation_img = dilation_img.resize(full_img.size, resample=Image.NEAREST)
    mask = output.resize(full_img.size, resample=Image.NEAREST)

    yellow_edge = Image.merge("RGB", (full_dilation_img, full_dilation_img, Image.new(mode="L", size=full_dilation_img.size)))
    outlined_img = full_img.copy()
    outlined_img.paste(yellow_edge, full_dilation_img)
    
    scores = [backgroundScore.numpy(), opmdScore.numpy(), osccScore.numpy()]
    return outlined_img, predictClass, scores, mask
