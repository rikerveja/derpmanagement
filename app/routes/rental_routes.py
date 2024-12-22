from flask import Blueprint, request, jsonify
from app.models import SerialNumber, UserContainer, UserHistory
from app.utils.email_utils import send_verification_email
from app.utils.logging_utils import log_operation
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
    try:
        # 查找所有已到期的租赁
        expired_rentals = SerialNumber.query.filter(
            SerialNumber.status == 'active',
            SerialNumber.used_at + timedelta(days=SerialNumber.duration_days) < datetime.utcnow()
        ).all()

        if not expired_rentals:
            log_operation(user_id=None, operation="rental_expiry", status="info", details="No expired rentals found.")
        
        for rental in expired_rentals:
            # 标记为到期
            rental.status = 'expired'

            # 删除用户的容器
            user_containers = UserContainer.query.filter_by(user_id=rental.user_id).all()
            for container in user_containers:
                db.session.delete(container)

            # 删除租赁历史记录
            user_history = UserHistory.query.filter_by(user_id=rental.user_id).all()
            for history in user_history:
                db.session.delete(history)

            log_operation(
                user_id=rental.user_id,
                operation="rental_expiry",
                status="success",
                details=f"Rental expired for user {rental.user_id} and resources released"
            )

        db.session.commit()
        return jsonify({"success": True, "message": "Expired rentals processed successfully"}), 200
    except Exception as e:
        db.session.rollback()  # 回滚事务
        log_operation(
            user_id=None,
            operation="rental_expiry",
            status="failed",
            details=f"Error processing expired rentals: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 发送租赁到期通知
@rental_bp.route('/api/rental/send_expiry_notifications', methods=['POST'])
def send_expiry_notifications():
    """
    发送即将到期的租赁通知
    """
    days_to_expiry = request.json.get('days_to_expiry', 7)
    try:
        expiring_rentals = SerialNumber.query.filter(
            SerialNumber.status == 'active',
            SerialNumber.used_at + timedelta(days=SerialNumber.duration_days - days_to_expiry) < datetime.utcnow()
        ).all()

        if not expiring_rentals:
            log_operation(user_id=None, operation="send_expiry_notification", status="info", details="No rentals expiring soon.")
        
        failed_emails = []
        for rental in expiring_rentals:
            user_email = rental.user.email
            email_sent = send_verification_email(user_email)  # 复用邮件发送逻辑，提醒用户续费

            if not email_sent:
                failed_emails.append(user_email)

            log_operation(
                user_id=rental.user_id,
                operation="send_expiry_notification",
                status="success",
                details=f"Expiry notification sent to {user_email}"
            )

        if failed_emails:
            logging.error(f"Failed to send reminder to: {', '.join(failed_emails)}")
            return jsonify({"success": False, "message": f"Failed to send reminders to: {', '.join(failed_emails)}"}), 500

        return jsonify({"success": True, "message": "Expiry notifications sent successfully"}), 200
    except Exception as e:
        log_operation(
            user_id=None,
            operation="send_expiry_notification",
            status="failed",
            details=f"Error sending expiry notifications: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Error sending notifications: {str(e)}"}), 500


# 用户续费接口
@rental_bp.route('/api/rental/renew', methods=['POST'])
def renew_rental():
    """
    用户续费接口
    """
    data = request.json
    serial_code = data.get('serial_code')

    if not serial_code:
        log_operation(
            user_id=None,
            operation="renew_rental",
            status="failed",
            details="Missing serial code"
        )
        return jsonify({"success": False, "message": "Missing serial code"}), 400

    try:
        # 查找对应的租赁
        rental = SerialNumber.query.filter_by(code=serial_code, status='active').first()
        if not rental:
            log_operation(
                user_id=None,
                operation="renew_rental",
                status="failed",
                details=f"Invalid or expired serial code: {serial_code}"
            )
            return jsonify({"success": False, "message": "Invalid or expired serial code"}), 404

        # 增加续租天数（默认为30天）
        rental.duration_days += data.get('additional_days', 30)
        db.session.commit()

        log_operation(
            user_id=rental.user_id,
            operation="renew_rental",
            status="success",
            details=f"Rental renewed for serial code {serial_code}"
        )
        return jsonify({"success": True, "message": "Rental renewed successfully"}), 200
    except Exception as e:
        db.session.rollback()  # 回滚事务
        log_operation(
            user_id=None,
            operation="renew_rental",
            status="failed",
            details=f"Error renewing rental: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 删除租赁信息（删除序列号及其关联的容器和历史记录）
@rental_bp.route('/api/rental/delete/<int:serial_id>', methods=['DELETE'])
def delete_rental(serial_id):
    """
    删除用户的租赁信息，包括序列号和关联的容器
    """
    try:
        rental = SerialNumber.query.get(serial_id)
        if not rental:
            return jsonify({"success": False, "message": "Rental not found"}), 404

        # 删除用户的容器
        user_containers = UserContainer.query.filter_by(user_id=rental.user_id).all()
        for container in user_containers:
            db.session.delete(container)

        # 删除租赁历史记录
        user_history = UserHistory.query.filter_by(user_id=rental.user_id).all()
        for history in user_history:
            db.session.delete(history)

        # 删除序列号
        db.session.delete(rental)
        db.session.commit()

        log_operation(
            user_id=rental.user_id,
            operation="delete_rental",
            status="success",
            details=f"Rental and associated containers deleted for user {rental.user_id}"
        )
        return jsonify({"success": True, "message": "Rental deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # 回滚事务
        log_operation(
            user_id=None,
            operation="delete_rental",
            status="failed",
            details=f"Error deleting rental: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Error deleting rental: {str(e)}"}), 500


# 查询用户租赁历史记录
@rental_bp.route('/api/rental/history/<int:user_id>', methods=['GET'])
def get_user_history(user_id):
    """
    查询用户租赁历史记录
    """
    try:
        user_history = UserHistory.query.filter_by(user_id=user_id).all()
        if not user_history:
            return jsonify({"success": False, "message": "No history found"}), 404

        history_data = [
            {
                "rental_start": record.rental_start,
                "rental_end": record.rental_end,
                "total_traffic": record.total_traffic,
            } for record in user_history
        ]
        return jsonify({"success": True, "history": history_data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching user history: {str(e)}"}), 500
