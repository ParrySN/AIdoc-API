# import secrets; print(secrets.token_hex())
SECRET_KEY='e3c527ed9640360190aea4b8438bf000351c648a46cfdaffa3a1dbfeda64db6d'

DB_HOST='icohold.anamai.moph.go.th' # To use ICOHOLD database, change this to 'icohold.anamai.moph.go.th' localhost
DB_DATABASE='aidoc_development'
DB_ORALCANCER='oralcancer'
DB_USER='patiwet'  # To use ICOHOLD database, change this to 'patiwet' root
DB_PASSWORD='icoh2017p@ssw0rd' # To use ICOHOLD database, change this to 'icoh2017p@ssw0rd'riskOCA@50200



# Maximum fize size to be uploaded (15MB)
MAX_CONTENT_LENGTH = 15 * 2**20

# Clear imageData/temp folder if #files in the temp folder is more than the threshold
CLEAR_TEMP_THRESHOLD = 50

# IMAGE_DATA_DIR is defined in the Flask factory (__init__.py)

# Admin password is 'riskOCA@50200' with a hash of scrypt:32768:8:1$fpQAbOlvB2esNbcl$b4458c49c97a506c51e4305c1e56dc67a2618eec7231fe5bf4eea35e9842405890632035c05c157013ef0e005cd5723a9c1d55478895718f9318b1cd80708d86
# Do not set admin to patient or osm to prevent data leak (their login is less secured)
ADMIN_USER_INSERT_SQL = "INSERT INTO `user` (`id`, `name`, `surname`, `national_id`, `email`, `phone`, `sex`, `birthdate`, `username`, `password`, `job_position`, `osm_job`, `hospital`, `province`, `address`, `license`, `is_patient`, `is_osm`, `is_specialist`, `is_admin`, `created_at`, `updated_at`, `default_sender_phone`, `default_location`) VALUES (NULL, 'ผู้ดูแลระบบ', 'Administrator', NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP, 'admin', 'scrypt:32768:8:1$fpQAbOlvB2esNbcl$b4458c49c97a506c51e4305c1e56dc67a2618eec7231fe5bf4eea35e9842405890632035c05c157013ef0e005cd5723a9c1d55478895718f9318b1cd80708d86', 'Computer Technical Officer', NULL, 'มหาวิทยาลัยเชียงใหม่', 'เชียงใหม่', NULL, NULL, '0', '0', '1', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, NULL)"
    