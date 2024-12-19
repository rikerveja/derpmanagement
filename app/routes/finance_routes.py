from flask import Blueprint, jsonify, request
from app.models import User, SerialNumber
from datetime import datetime
from sqlalchemy import func
from app import db
import random
import string

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/statistics', methods=['GET'])
def finance_statistics():
    """
    获取财务统计数据
    """
    total_revenue = SerialNumber.query.with_entities(func.sum(SerialNumber.duration_days)).scalar() or 0
    return jsonify({
        "success": True,
        "total_revenue": total_revenue,
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@finance_bp.route('/orders/<int:user_id>', methods=['GET'])
def user_orders(user_id):
    """
    获取用户订单记录
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    orders = [
        {
            "serial_number": sn.code,
            "status": sn.status,
            "duration_days": sn.duration_days,
            "created_at": sn.created_at.isoformat(),
            "used_at": sn.used_at.isoformat() if sn.used_at else None
        }
        for sn in user.serial_numbers
    ]
    return jsonify({"success": True, "orders": orders}), 200


@finance_bp.route('/generate_serial', methods=['POST'])
def generate_serial():
    """
    管理员生成序列号
    """
    data = request.json
    duration_days = data.get('duration_days')
    count = data.get('count', 1)

    if not duration_days:
        return jsonify({"success": False, "message": "Missing duration_days"}), 400

    serial_numbers = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        serial_number = SerialNumber(code=code, duration_days=duration_days)
        db.session.add(serial_number)
        serial_numbers.append(code)

    try:
        db.session.commit()
        return jsonify({"success": True, "serial_numbers": serial_numbers}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@finance_bp.route('/serial_numbers', methods=['GET'])
def list_serial_numbers():
    """
    查看所有序列号
    """
    serial_numbers = SerialNumber.query.all()
    result = [
        {
            "code": sn.code,
            "duration_days": sn.duration_days,
            "status": sn.status,
            "created_at": sn.created_at.isoformat(),
            "used_at": sn.used_at.isoformat() if sn.used_at else None
        }
        for sn in serial_numbers
    ]
    return jsonify({"success": True, "serial_numbers": result}), 200
