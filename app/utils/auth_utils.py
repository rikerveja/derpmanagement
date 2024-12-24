import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config import Config
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_utils")

# 加密密码
def hash_password(password):
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        logger.info("Password hashed successfully.")
        return hashed
    except Exception as e:
        logger.exception("Error hashing password.")
        raise

# 验证密码
def check_password(password, hashed_password):
    try:
        result = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        logger.info(f"Password check {'succeeded' if result else 'failed'}.")
        return result
    except Exception as e:
        logger.exception("Error checking password.")
        return False

# 生成 JWT
def generate_jwt(payload, expiration_hours=24):
    try:
        payload['exp'] = datetime.utcnow() + timedelta(hours=expiration_hours)
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        logger.info("JWT generated successfully.")
        return token
    except Exception as e:
        logger.exception("Error generating JWT.")
        raise

# 解码 JWT
def decode_jwt(token):
    try:
        decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        logger.info("JWT decoded successfully.")
        return decoded
    except jwt.ExpiredSignatureError:
        logger.warning("JWT has expired.")
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT: {e}")
        return {"error": f"Invalid token: {e}"}
    except Exception as e:
        logger.exception("Error decoding JWT.")
        return {"error": f"Error decoding JWT: {str(e)}"}

# 生成刷新令牌
def generate_refresh_token(user_id, expiration_days=7):
    """
    为用户生成一个刷新令牌。
    默认过期时间为 7 天。
    """
    try:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=expiration_days)
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        logger.info("Refresh token generated successfully.")
        return token
    except Exception as e:
        logger.exception("Error generating refresh token.")
        raise
