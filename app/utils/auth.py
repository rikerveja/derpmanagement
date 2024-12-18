import bcrypt
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"  # 你可以通过 .env 文件设置并加载 SECRET_KEY

# 用于加密密码
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# 用于校验密码
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# 生成 JWT Token
def generate_jwt(payload, expiration=24):
    payload['exp'] = datetime.utcnow() + timedelta(hours=expiration)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
