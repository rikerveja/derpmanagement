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
    """
    使用 bcrypt 对密码进行加密。
    """
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')  # 控制复杂度
        logger.info("Password hashed successfully.")
        return hashed
    except Exception as e:
        logger.exception("Error hashing password.")  # 更详细的日志记录
        raise

# 验证密码
def check_password(password, hashed_password):
    """
    验证用户提供的密码是否与存储的哈希密码匹配。
    """
    try:
        result = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        logger.info(f"Password check {'succeeded' if result else 'failed'}.")
        return result
    except Exception as e:
        logger.exception("Error checking password.")  # 更详细的日志记录
        return False

# 生成 JWT
def generate_jwt(payload, expiration_hours=24):
    """
    生成包含指定负载的 JWT。
    默认过期时间为 24 小时。
    """
    try:
        payload['exp'] = datetime.utcnow() + timedelta(hours=expiration_hours)
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        logger.info("JWT generated successfully.")
        return token
    except Exception as e:
        logger.exception("Error generating JWT.")  # 更详细的日志记录
        raise

# 解码 JWT
def decode_jwt(token):
    """
    解码 JWT 并验证其有效性。
    """
    try:
        decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        logger.info("JWT decoded successfully.")
        return decoded
    except jwt.ExpiredSignatureError:
        logger.warning("JWT has expired.")  # 专门处理过期情况
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT: {e}")  # 捕获更多异常
        return {"error": f"Invalid token: {e}"}
