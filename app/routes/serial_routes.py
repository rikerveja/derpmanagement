from flask import Blueprint, jsonify, request
from app.models import SerialNumber, db
import random
import string
from datetime import datetime, timedelta

# 定义蓝图
serial_bp = Blueprint('serial', __name__)

# 生成序列号
@serial_bp.route('/api/serial/generate', methods=['POST'])
def generate_serial():
    """
    生成序列号
    """
    data = request.json
    count = data.get('count', 1)
    duration_days = data.get('duration_days', 30)
    serial_length = data.get('serial_length', 12)  # 新增：序列号长度参数，默认12位

    if count <= 0 or duration_days <= 0 or serial_length <= 0:
        return jsonify({"success": False, "message": "Invalid parameters"}), 400

    serial_numbers = []
    for _ in range(count):
        # 确保序列号唯一性
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=serial_length))
            existing_serial = SerialNumber.query.filter_by(code=code).first()
            if not existing_serial:  # 如果序列号不重复，跳出循环
                break
        
        # 设置序列号的默认状态为 "unused"
        expires_at = datetime.utcnow() + timedelta(days=duration_days)
        serial_number = SerialNumber(code=code, duration_days=duration_days, status='unused', expires_at=expires_at)
        db.session.add(serial_number)
        serial_numbers.append(code)

    db.session.commit()
    return jsonify({"success": True, "serial_numbers": serial_numbers}), 201


# 检查序列号状态
@serial_bp.route('/api/serial/check/<serial_code>', methods=['GET'])
def check_serial(serial_code):
    """
    检查序列号状态
    """
    serial_number = SerialNumber.query.filter_by(code=serial_code).first()
    if not serial_number:
        return jsonify({"success": False, "message": "Serial number not found"}), 404

    # 检查序列号是否过期
    current_time = datetime.utcnow()
    expired = serial_number.expires_at < current_time if serial_number.expires_at else False

    # 返回序列号的详细信息
    return jsonify({
        "success": True,
        "serial_code": serial_number.code,
        "status": serial_number.status,
        "duration_days": serial_number.duration_days,
        "created_at": serial_number.created_at.isoformat(),
        "expires_at": serial_number.expires_at.isoformat() if serial_number.expires_at else None,
        "expired": expired
    }), 200
