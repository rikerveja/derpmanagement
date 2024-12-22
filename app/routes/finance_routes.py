from flask import Blueprint, jsonify, request
from app.models import User, SerialNumber
from datetime import datetime
from sqlalchemy import func
from app import db
import random
import string

finance_bp = Blueprint('finance', __name__)

# 获取财务统计数据
@finance_bp.route('/statistics', methods=['GET'])
def finance_statistics():
    """
    获取财务统计数据，包括总收入（基于序列号的天数）和每个用户的总收入
    """
    try:
        # 总收入 = 所有序列号的持续天数总和
        total_revenue = SerialNumber.query.with_entities(func.sum(SerialNumber.duration_days)).scalar() or 0

        # 获取每个用户的收入
        user_revenue = db.session.query(
            User.id,
            User.username,
            func.sum(SerialNumber.duration_days).label("total_revenue")
        ).join(SerialNumber).group_by(User.id).all()

        user_revenue_data = [
            {"user_id": user.id, "username": user.username, "total_revenue": user.total_revenue}
            for user in user_revenue
        ]

        return jsonify({
            "success": True,
            "total_revenue": total_revenue,
            "user_revenue": user_revenue_data,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching financial statistics: {str(e)}"}), 500


# 获取用户订单记录
@finance_bp.route('/orders/<int:user_id>', methods=['GET'])
def user_orders(user_id):
    """
    获取用户订单记录，包括用户的所有序列号
    """
    try:
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
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching orders: {str(e)}"}), 500


# 管理员生成序列号
@finance_bp.route('/generate_serial', methods=['POST'])
def generate_serial():
    """
    管理员生成序列号
    """
    data = request.json
    duration_days = data.get('duration_days')
    count = data.get('count', 1)

    # 检查必填字段
    if not duration_days:
        return jsonify({"success": False, "message": "Missing duration_days"}), 400

    serial_numbers = []
    try:
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            serial_number = SerialNumber(code=code, duration_days=duration_days)
            db.session.add(serial_number)
            serial_numbers.append(code)

        db.session.commit()
        return jsonify({"success": True, "serial_numbers": serial_numbers}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 查看所有序列号
@finance_bp.route('/serial_numbers', methods=['GET'])
def list_serial_numbers():
    """
    查看所有序列号，包括序列号的状态和关联用户的信息
    """
    try:
        serial_numbers = SerialNumber.query.all()
        result = [
            {
                "code": sn.code,
                "duration_days": sn.duration_days,
                "status": sn.status,
                "created_at": sn.created_at.isoformat(),
                "used_at": sn.used_at.isoformat() if sn.used_at else None,
                "user_id": sn.user_id,  # 关联的用户 ID
                "user_username": sn.user.username if sn.user else None  # 用户名
            }
            for sn in serial_numbers
        ]
        return jsonify({"success": True, "serial_numbers": result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching serial numbers: {str(e)}"}), 500


# 获取用户的财务信息
@finance_bp.route('/user_finance/<int:user_id>', methods=['GET'])
def get_user_finance(user_id):
    """
    获取用户的财务信息，包括用户的总收入和订单详情
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # 获取该用户的所有序列号
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
        
        # 计算该用户的总收入（基于序列号的天数）
        total_revenue = sum(sn.duration_days for sn in user.serial_numbers)

        return jsonify({
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "total_revenue": total_revenue,
            "orders": orders
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching user finance details: {str(e)}"}), 500
