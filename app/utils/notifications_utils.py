import os
from flask_mail import Message
from app import mail
from app.models import User, SerialNumber
from datetime import datetime, timedelta
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        return False


def send_rental_expiry_notifications(days_to_expiry=7):
    """
    发送租赁到期提醒通知
    :param days_to_expiry: 租赁到期前的天数
    """
    try:
        now = datetime.utcnow()
        expiry_threshold = now + timedelta(days=days_to_expiry)

        # 查询即将到期的租赁
        expiring_rentals = SerialNumber.query.filter(
            SerialNumber.status == 'active',
            SerialNumber.used_at + timedelta(days=SerialNumber.duration_days) <= expiry_threshold,
            SerialNumber.used_at + timedelta(days=SerialNumber.duration_days) > now
        ).all()

        if not expiring_rentals:
            logger.info("No rentals expiring within the specified time frame.")
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
                logger.info(f"Rental expiry notification sent to {user_email}")
            else:
                logger.error(f"Failed to send rental expiry notification to {user_email}")
    except Exception as e:
        logger.error(f"Error sending rental expiry notifications: {str(e)}")
        logger.error(e, exc_info=True)


def send_general_notification(user_id, subject, body):
    """
    发送通用通知给指定用户
    :param user_id: 用户 ID
    :param subject: 通知主题
    :param body: 通知内容
    :return: bool (True 表示发送成功，False 表示失败)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User with ID {user_id} not found.")
            return False

        return send_email(user.email, subject, body)
    except Exception as e:
        logger.error(f"Error sending general notification to user {user_id}: {str(e)}")
        logger.error(e, exc_info=True)
        return False


def send_bulk_notifications(users, subject, body_template):
    """
    批量发送通知
    :param users: 用户列表 (User 模型实例列表)
    :param subject: 通知主题
    :param body_template: 通知模板 (支持字符串格式化，例如 {username})
    """
    try:
        for user in users:
            body = body_template.format(username=user.username, email=user.email)
            if send_email(user.email, subject, body):
                logger.info(f"Notification sent to {user.email}")
            else:
                logger.error(f"Failed to send notification to {user.email}")
    except Exception as e:
        logger.error(f"Error sending bulk notifications: {str(e)}")
        logger.error(e, exc_info=True)


def send_notification_email(recipient, subject, body):
    """
    发送通知邮件（提供简单封装）
    :param recipient: 收件人邮箱
    :param subject: 邮件主题
    :param body: 邮件内容
    :return: bool (True 表示发送成功，False 表示失败)
    """
    return send_email(recipient, subject, body)
