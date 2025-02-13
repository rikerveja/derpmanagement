from flask import Blueprint, jsonify, request
from flask_mail import Message
from app import mail, db
from app.models import User, NotificationLog
from datetime import datetime, timedelta
from app.utils.notifications_utils import send_email
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

    try:
        # 查询即将到期的用户
        expiring_users = User.query.filter(User.rental_expiry <= expiry_threshold, User.rental_expiry > now).all()

        if not expiring_users:
            logging.info("No users with expiring rentals found.")
            return jsonify({"success": True, "message": "No users with expiring rentals"}), 200

        failed_emails = []
        for user in expiring_users:
            email_subject = "Your rental service is expiring soon"
            email_body = (
                f"Dear {user.username},\n\n"
                f"Your rental service will expire on {user.rental_expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC. "
                f"Please renew your service to avoid interruptions.\n\n"
                f"Thank you for using our service."
            )

            # 使用通用邮件发送工具
            email_sent = send_email(user.email, email_subject, email_body)
            if not email_sent:
                failed_emails.append(user.email)
                # 记录通知失败的日志
                notification_log = NotificationLog(
                    user_id=user.id,
                    subject=email_subject,
                    body=email_body,
                    status="failed",
                    error_message="Failed to send email"
                )
                db.session.add(notification_log)
            else:
                # 记录通知成功的日志
                notification_log = NotificationLog(
                    user_id=user.id,
                    subject=email_subject,
                    body=email_body,
                    status="success"
                )
                db.session.add(notification_log)

        # 提交所有日志到数据库
        db.session.commit()

        if failed_emails:
            logging.error(f"Failed to send reminder to: {', '.join(failed_emails)}")
            return jsonify({"success": False, "message": f"Failed to send reminders to some users: {failed_emails}"}), 500

        logging.info("Reminder emails sent successfully.")
        return jsonify({"success": True, "message": "Reminder emails sent successfully"}), 200

    except Exception as e:
        # 捕获异常并记录日志
        logging.error(f"Error occurred while sending reminder emails: {str(e)}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
