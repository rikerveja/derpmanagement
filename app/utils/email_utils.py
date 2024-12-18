from flask_mail import Message
from app import mail

# 邮箱验证码存储（开发中可以用内存，生产建议使用 Redis）
email_verification_store = {}

# 发送验证码到用户邮箱
def send_verification_email(email, code):
    try:
        msg = Message(
            subject="Your Verification Code",
            sender="your_email@example.com",  # 替换为你的发送邮箱
            recipients=[email]
        )
        msg.body = f"Your verification code is: {code}"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# 验证用户输入的验证码是否正确
def validate_verification_code(email, code):
    stored_code = email_verification_store.get(email)
    if stored_code and stored_code == code:
        # 如果验证码验证通过，删除存储的验证码
        del email_verification_store[email]
        return True
    return False
