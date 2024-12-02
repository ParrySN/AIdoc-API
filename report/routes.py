from flask import request, Blueprint
import db
from report import report

report_bp = Blueprint('report', __name__)


@report_bp.route('/report/', methods=['GET'])
def getReport():
    province = request.args.get('province')
    return report.report(province)
