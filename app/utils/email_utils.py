import random
import string
import logging
from flask_mail import Message
from app import mail
import os
import redis

# 初始化 Redis 连接
redis_client = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)

# 日志配置
logging.basicConfig(level=logging.INFO)

# 生成随机验证码
def generate_verification_code(length=6):
    """
    生成指定长度的随机数字验证码
    """
    return ''.join(random.choices(string.digits, k=length))

# 发送邮箱验证码
def send_verification_email(email):
    """
    向指定邮箱发送验证码邮件
    """
    verification_code = generate_verification_code()

    # 将验证码存储到 Redis，设置过期时间（默认 5 分钟）
    try:
        redis_client.setex(f"verification_code:{email}", 300, verification_code)
        logging.info(f"Verification code for {email} stored in Redis.")

        # 构建邮件内容
        msg = Message(
            subject="Your Verification Code",
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[email]
        )
        msg.body = f"Your verification code is: {verification_code}"

        # 发送邮件
        mail.send(msg)
        logging.info(f"Verification email sent to {email}")
        return True
    except Exception as e:
        logging.error(f"Error sending verification email to {email}: {e}")
        return False

# 验证邮箱验证码
def validate_verification_code(email, code):
    """
    验证用户输入的验证码是否正确
    """
    try:
        stored_code = redis_client.get(f"verification_code:{email}")
        if stored_code and stored_code.decode('utf-8') == code:
            redis_client.delete(f"verification_code:{email}")
            logging.info(f"Verification code for {email} validated successfully.")
            return True
        logging.warning(f"Invalid or expired verification code for {email}.")
        return False
    except Exception as e:
        logging.error(f"Error validating verification code for {email}: {e}")
        return False
