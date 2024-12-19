from flask import Blueprint, request, jsonify
from app.models import SerialNumber, UserContainer
from app.utils.email_utils import send_verification_email
from app import db
from datetime import datetime, timedelta

# 定义蓝图
rental_bp = Blueprint('rental', __name__)

# 检查租赁到期用户并释放资源
@rental_bp.route('/api/rental/check_expiry', methods=['GET'])
def check_expiry():
    """
    检测租赁到期的用户并释放资源
    """
    expired_rentals = SerialNumber.query.filter(
        SerialNumber.status == 'active',
        SerialNumber.used_at + timedelta(days=SerialNumber.duration_days) < datetime.utcnow()
    ).all()

    for rental in expired_rentals:
        # 标记为到期
        rental.status = 'expired'

        # 删除用户的容器
        user_containers = UserContainer.query.filter_by(user_id=rental.user_id).all()
        for container in user_containers:
            db.session.delete(container)

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Expired rentals processed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 发送租赁到期通知
@rental_bp.route('/api/rental/send_expiry_notifications', methods=['POST'])
def send_expiry_notifications():
    """
    发送即将到期的租赁通知
    """
    days_to_expiry = request.json.get('days_to_expiry', 7)
    expiring_rentals = SerialNumber.query.filter(
        SerialNumber.status == 'active',
        SerialNumber.used_at + timedelta(days=SerialNumber.duration_days - days_to_expiry) < datetime.utcnow()
    ).all()

    for rental in expiring_rentals:
        user_email = rental.user.email
        send_verification_email(user_email)  # 复用邮件发送逻辑，提醒用户续费

    return jsonify({"success": True, "message": "Expiry notifications sent successfully"}), 200


# 用户续费接口
@rental_bp.route('/api/rental/renew', methods=['POST'])
def renew_rental():
    """
    用户续费接口
    """
    data = request.json
    serial_code = data.get('serial_code')

    if not serial_code:
        return jsonify({"success": False, "message": "Missing serial code"}), 400

    rental = SerialNumber.query.filter_by(code=serial_code, status='active').first()
    if not rental:
        return jsonify({"success": False, "message": "Invalid or expired serial code"}), 404

    try:
        rental.duration_days += data.get('additional_days', 30)  # 默认续费 30 天
        db.session.commit()
        return jsonify({"success": True, "message": "Rental renewed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
