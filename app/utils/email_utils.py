import random
import string
import time
from flask_mail import Message
from flask import current_app
from app import mail

# 临时存储邮箱验证码（建议生产环境用 Redis 替代）
email_verification_store = {}

# 生成随机验证码
def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# 发送邮箱验证码
def send_verification_email(email):
    verification_code = generate_verification_code()
    timestamp = int(time.time())  # 当前时间戳
    email_verification_store[email] = {"code": verification_code, "timestamp": timestamp}

    try:
        msg = Message(
            subject="Your Verification Code",
            sender=current_app.config["MAIL_USERNAME"],  # 从配置加载发件邮箱
            recipients=[email]
        )
        msg.body = f"Your verification code is: {verification_code}"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# 验证邮箱验证码（增加有效期检查）
def validate_verification_code(email, code, valid_duration=300):
    """验证邮箱验证码是否正确和未过期
    :param email: 收件邮箱地址
    :param code: 用户输入的验证码
    :param valid_duration: 验证码有效期，单位秒（默认 300 秒）
    :return: 验证成功返回 True，失败返回 False
    """
    data = email_verification_store.get(email)
    if not data:
        return False  # 验证码不存在

    stored_code = data.get("code")
    timestamp = data.get("timestamp")

    if stored_code != code:
        return False  # 验证码不匹配

    # 检查验证码是否过期
    current_time = int(time.time())
    if current_time - timestamp > valid_duration:
        del email_verification_store[email]  # 删除过期验证码
        return False

    del email_verification_store[email]  # 验证成功后删除验证码
    return True
