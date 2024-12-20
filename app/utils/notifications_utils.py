import os
from flask_mail import Message
from app import mail
from app.models import User, SerialNumber
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

def send_email(recipient, subject, body):
    """
    通用函数，用于发送邮件
    :param recipient: 接收方邮箱地址
    :param subject: 邮件主题
    :param body: 邮件内容
    :return: bool (True 表示发送成功，False 表示失败)
    """
    try:
        msg = Message(
            subject=subject,
            sender=os.getenv('MAIL_USERNAME'),  # 从环境变量中获取发件人
            recipients=[recipient]
        )
        msg.body = body
        mail.send(msg)
        logging.info(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {str(e)}")
        return False

def send_rental_expiry_notifications(days_to_expiry=7):
    """
    发送租赁到期提醒通知
    :param days_to_expiry: 租赁到期前的天数
    """
    now = datetime.utcnow()
    expiry_threshold = now + timedelta(days=days_to_expiry)

    # 查询即将到期的租赁
    expiring_rentals = SerialNumber.query.filter(
        SerialNumber.status == 'active',
        SerialNumber.used_at + timedelta(days=SerialNumber.duration_days) <= expiry_threshold,
        SerialNumber.used_at + timedelta(days=SerialNumber.duration_days) > now
    ).all()

    if not expiring_rentals:
        logging.info("No rentals expiring within the specified time frame.")
        return

    for rental in expiring_rentals:
        user_email = rental.user.email
        subject = "Your Rental is About to Expire"
        body = (
            f"Dear {rental.user.username},\n\n"
            f"Your rental with code {rental.code} is about to expire on "
            f"{(rental.used_at + timedelta(days=rental.duration_days)).strftime('%Y-%m-%d %H:%M:%S')} UTC. "
            "Please renew your rental to avoid service interruption.\n\n"
            "Thank you."
        )
        if send_email(user_email, subject, body):
            logging.info(f"Rental expiry notification sent to {user_email}")
        else:
            logging.error(f"Failed to send rental expiry notification to {user_email}")

def send_general_notification(user_id, subject, body):
    """
    发送通用通知给指定用户
    :param user_id: 用户 ID
    :param subject: 通知主题
    :param body: 通知内容
    :return: bool (True 表示发送成功，False 表示失败)
    """
    user = User.query.get(user_id)
    if not user:
        logging.error(f"User with ID {user_id} not found.")
        return False

    return send_email(user.email, subject, body)

def send_bulk_notifications(users, subject, body_template):
    """
    批量发送通知
    :param users: 用户列表 (User 模型实例列表)
    :param subject: 通知主题
    :param body_template: 通知模板 (支持字符串格式化，例如 {username})
    """
    for user in users:
        body = body_template.format(username=user.username, email=user.email)
        if send_email(user.email, subject, body):
            logging.info(f"Notification sent to {user.email}")
        else:
            logging.error(f"Failed to send notification to {user.email}")


from flask_mail import Message
from app import mail
import logging
import os

logging.basicConfig(level=logging.INFO)

def send_notification_email(recipient, subject, body):
    """
    发送通知邮件
    :param recipient: 收件人邮箱
    :param subject: 邮件主题
    :param body: 邮件内容
    """
    try:
        msg = Message(
            subject=subject,
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[recipient]
        )
        msg.body = body
        mail.send(msg)
        logging.info(f"Notification email sent to {recipient}")
    except Exception as e:
        logging.error(f"Failed to send notification email to {recipient}: {e}")

