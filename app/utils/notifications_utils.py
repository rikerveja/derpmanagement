import os
from flask_mail import Message
from app import mail
from app.models import User, SerialNumber
from datetime import datetime, timedelta

def send_notification_email(email, subject, body):
    """
    通用函数，用于发送通知邮件
    :param email: 接收方邮箱地址
    :param subject: 邮件主题
    :param body: 邮件内容
    """
    try:
        msg = Message(
            subject=subject,
            sender=os.getenv('MAIL_USERNAME'),  # 从环境变量中获取发件人
            recipients=[email]
        )
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send notification email to {email}: {e}")
        return False

def send_rental_expiry_notifications(days_to_expiry=7):
    """
    发送租赁到期提醒通知
    :param days_to_expiry: 租赁到期前的天数
    """
    expiring_rentals = SerialNumber.query.filter(
        SerialNumber.status == 'active',
        SerialNumber.used_at + timedelta(days=SerialNumber.duration_days - days_to_expiry) < datetime.utcnow()
    ).all()

    for rental in expiring_rentals:
        user_email = rental.user.email
        subject = "Your Rental is About to Expire"
        body = (
            f"Dear {rental.user.username},\n\n"
            f"Your rental with code {rental.code} is about to expire in {days_to_expiry} days. "
            "Please renew your rental to avoid interruption of service.\n\n"
            "Thank you."
        )
        send_notification_email(user_email, subject, body)

def send_general_notification(user_id, subject, body):
    """
    发送通用通知给指定用户
    :param user_id: 用户 ID
    :param subject: 通知主题
    :param body: 通知内容
    """
    user = User.query.get(user_id)
    if not user:
        print(f"User with ID {user_id} not found.")
        return False

    return send_notification_email(user.email, subject, body)
