def map_job_position_to_th(job_position):
    job_position_dict = {
        "OSM": "อสม.",
        "Dental Nurse": "ทันตาภิบาล/เจ้าพนักงานทันตสาธารณสุข",
        "Dentist": "ทันตแพทย์",
        "Oral Pathologist": "ทันตแพทย์เฉพาะทาง วิทยาการวินิจฉัยโรคช่องปาก",
        "Oral and Maxillofacial Surgeon": "ทันตแพทย์เฉพาะทาง ศัลยศาสตร์ช่องปากและแม็กซิลโลเฟเชียล",
        "Physician": "แพทย์",
        "Public Health Technical Officer": "นักวิชาการสาธารณสุข",
        "Computer Technical Officer": "นักวิชาการคอมพิวเตอร์/นักวิจัย/ผู้พัฒนาระบบ",
        "Other Public Health Officer": "ข้าราชการ/เจ้าพนักงานกระทรวงสาธารณสุข",
        "Other Government Officer": "เจ้าหน้าที่รัฐอื่น",
        "General Public": "บุคคลทั่วไป"
    }
    return job_position_dict.get(job_position, "Unknown Position")