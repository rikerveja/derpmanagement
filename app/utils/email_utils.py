import random
import string
import logging
from flask_mail import Message
from app import mail
import os
import redis
import traceback
from datetime import datetime

# 初始化 Redis 连接
redis_client = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 生成随机验证码
def generate_verification_code(length=6, use_letters=False):
    """
    生成指定长度的随机验证码（数字或字母数字组合）
    :param length: 验证码长度
    :param use_letters: 是否包括字母
    """
    try:
        characters = string.digits
        if use_letters:
            characters += string.ascii_letters  # 包括字母
        code = ''.join(random.choices(characters, k=length))
        logger.info(f"Generated verification code: {code}")
        return code
    except Exception as e:
        logger.error(f"Error generating verification code: {e}")
        logger.error(traceback.format_exc())
        return None

# 发送邮箱验证码
def send_verification_email(email, use_letters=False):
    """
    向指定邮箱发送验证码邮件
    :param email: 收件邮箱
    :param use_letters: 是否使用字母组成验证码
    """
    verification_code = generate_verification_code(use_letters=use_letters)

    if not verification_code:
        logger.error("Failed to generate verification code.")
        return False

    try:
        # 将验证码存储到 Redis，设置过期时间（默认 5 分钟）
        redis_client.setex(f"verification_code:{email}", 300, verification_code)
        logger.info(f"Verification code for {email} stored in Redis.")

        # 构建邮件内容
        msg = Message(
            subject="Your Verification Code",
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[email]
        )
        msg.body = f"Your verification code is: {verification_code}"

        # 发送邮件
        mail.send(msg)
        logger.info(f"Verification email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending verification email to {email}: {e}")
        logger.error(traceback.format_exc())
        return False

# 验证邮箱验证码
def validate_verification_code(email, code):
    """
    验证用户输入的验证码是否正确
    :param email: 用户的邮箱
    :param code: 用户输入的验证码
    """
    try:
        stored_code = redis_client.get(f"verification_code:{email}")
        if stored_code:
            stored_code = stored_code.decode('utf-8')
            if stored_code == code:
                redis_client.delete(f"verification_code:{email}")  # 验证成功后删除验证码
                logger.info(f"Verification code for {email} validated successfully.")
                return True
            else:
                logger.warning(f"Invalid verification code for {email}.")
                return False
        logger.warning(f"Verification code for {email} has expired or not found.")
        return False
    except Exception as e:
        logger.error(f"Error validating verification code for {email}: {e}")
        logger.error(traceback.format_exc())
        return False

# 发送续费提醒邮件
def send_expiry_notification(email, days_to_expiry, expiry_date, **kwargs):
    """
    发送续费提醒邮件 - 纯通知功能，不需要验证码
    :param email: 收件邮箱
    :param days_to_expiry: 剩余天数
    :param expiry_date: 到期时间
    """
    try:
        subject = "您的服务即将到期"
        body = f"""
尊敬的用户：

您好！我们注意到您的服务即将到期，为了确保您的服务不会中断，请及时续费。

- 到期时间：{expiry_date}
- 剩余天数：{days_to_expiry}天

请登录管理面板或者联系管理员278557855@qq.com完成续费操作。
如已续费请忽略此提醒。

若有任何问题，请随时联系客服18057153331。
        """

        msg = Message(
            subject=subject,
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[email]
        )
        msg.body = body

        # 直接发送邮件，不涉及验证码和 Redis
        mail.send(msg)
        logger.info(f"Expiry notification sent to {email}")
        return True

    except Exception as e:
        logger.error(f"Error sending expiry notification to {email}: {e}")
        logger.error(traceback.format_exc())
        return False
