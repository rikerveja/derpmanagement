from flask import Blueprint, jsonify, request
from app.models import User, SerialNumber
from datetime import datetime
from sqlalchemy import func
from app import db

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/statistics', methods=['GET'])
def finance_statistics():
    """
    获取财务统计数据
    """
    # 示例数据：计算总收益
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
