from flask_mail import Message
from app import mail

email_verification_store = {}

def send_verification_email(email):
    code = "123456"  # Generate random code here
    email_verification_store[email] = code
    try:
        msg = Message("Your Verification Code", sender="your_email@example.com", recipients=[email])
        msg.body = f"Your verification code is: {code}"
        mail.send(msg)
        return True
    except Exception:
        return False

def validate_verification_code(email, code):
    return email_verification_store.get(email) == code
