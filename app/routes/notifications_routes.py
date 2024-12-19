from flask import Blueprint, jsonify, request
from flask_mail import Message
from app import mail, db
from app.models import User
from datetime import datetime, timedelta
import logging

notifications_bp = Blueprint('notifications', __name__)
logging.basicConfig(level=logging.INFO)

# 发送租赁到期提醒
@notifications_bp.route('/api/notifications/send_reminder', methods=['POST'])
def send_reminder():
    """
    扫描即将到期的用户租赁，并发送提醒邮件
    """
    days_before_expiry = request.json.get('days_before_expiry', 3)  # 默认提前3天提醒
    now = datetime.utcnow()
    expiry_threshold = now + timedelta(days=days_before_expiry)

    # 查询即将到期的用户
    expiring_users = User.query.filter(User.rental_expiry <= expiry_threshold, User.rental_expiry > now).all()

    if not expiring_users:
        logging.info("No users with expiring rentals found.")
        return jsonify({"success": True, "message": "No users with expiring rentals"}), 200

    for user in expiring_users:
        try:
            msg = Message(
                subject="Your rental service is expiring soon",
                sender="noreply@example.com",
                recipients=[user.email],
                body=f"Dear {user.username},\n\nYour rental service will expire on {user.rental_expiry}. Please renew your service to avoid interruptions."
            )
            mail.send(msg)
            logging.info(f"Reminder sent to {user.email}")
        except Exception as e:
            logging.error(f"Failed to send email to {user.email}: {str(e)}")
            return jsonify({"success": False, "message": f"Failed to send email to {user.email}: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Reminder emails sent successfully"}), 200
