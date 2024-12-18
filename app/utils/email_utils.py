import random
import string
from flask_mail import Message
from app import mail

# 临时存储邮箱验证码（建议生产环境用 Redis 替代）
email_verification_store = {}

# 生成随机验证码
def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# 发送邮箱验证码
def send_verification_email(email):
    verification_code = generate_verification_code()
    email_verification_store[email] = verification_code  # 暂存验证码

    try:
        msg = Message(
            subject="Your Verification Code",
            sender="your_email@example.com",  # 修改为你的邮箱
            recipients=[email]
        )
        msg.body = f"Your verification code is: {verification_code}"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# 验证邮箱验证码
def validate_verification_code(email, code):
    stored_code = email_verification_store.get(email)
    if stored_code and stored_code == code:
        del email_verification_store[email]  # 验证成功后删除验证码
        return True
    return False
