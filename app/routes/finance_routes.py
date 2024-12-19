# app/routes/finance_routes.py
from flask import Blueprint, request, jsonify
from app.models.finance import SerialNumber
from app import db
import random
import string

finance_bp = Blueprint('finance', __name__)

# 生成序列号
@finance_bp.route('/api/generate_serial', methods=['POST'])
def generate_serial():
    data = request.json
    duration_days = data.get('duration_days')

    if not duration_days or not isinstance(duration_days, int):
        return jsonify({"success": False, "message": "Invalid duration"}), 400

    # 生成随机序列号
    serial_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    serial = SerialNumber(code=serial_code, duration_days=duration_days)

    db.session.add(serial)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Serial generated successfully", "serial_code": serial_code}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
