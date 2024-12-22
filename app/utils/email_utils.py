import random
import string
import logging
from flask_mail import Message
from app import mail
import os
import redis
import traceback

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
        logger.error(traceback.format_exc())  # 记录详细的异常信息
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

    # 将验证码存储到 Redis，设置过期时间（默认 5 分钟）
    try:
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
    except redis.RedisError as redis_error:
        logger.error(f"Error interacting with Redis: {redis_error}")
        logger.error(traceback.format_exc())  # 记录 Redis 错误信息
    except Exception as e:
        logger.error(f"Error sending verification email to {email}: {e}")
        logger.error(traceback.format_exc())  # 记录详细的异常信息
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
    except redis.RedisError as redis_error:
        logger.error(f"Error interacting with Redis: {redis_error}")
        logger.error(traceback.format_exc())  # 记录 Redis 错误信息
        return False
    except Exception as e:
        logger.error(f"Error validating verification code for {email}: {e}")
        logger.error(traceback.format_exc())  # 记录详细的异常信息
        return False
