from flask import Blueprint, jsonify, request
from app.models import SerialNumber, db
import random
import string

# 定义蓝图
serial_bp = Blueprint('serial', __name__)

@serial_bp.route('/api/serial/generate', methods=['POST'])
def generate_serial():
    """
    生成序列号
    """
    data = request.json
    count = data.get('count', 1)
    duration_days = data.get('duration_days', 30)

    if count <= 0 or duration_days <= 0:
        return jsonify({"success": False, "message": "Invalid parameters"}), 400

    serial_numbers = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        serial_number = SerialNumber(code=code, duration_days=duration_days)
        db.session.add(serial_number)
        serial_numbers.append(code)

    db.session.commit()
    return jsonify({"success": True, "serial_numbers": serial_numbers}), 201

@serial_bp.route('/api/serial/check/<serial_code>', methods=['GET'])
def check_serial(serial_code):
    """
    检查序列号状态
    """
    serial_number = SerialNumber.query.filter_by(code=serial_code).first()
    if not serial_number:
        return jsonify({"success": False, "message": "Serial number not found"}), 404

    return jsonify({
        "success": True,
        "serial_code": serial_number.code,
        "status": serial_number.status,
        "duration_days": serial_number.duration_days
    }), 200
