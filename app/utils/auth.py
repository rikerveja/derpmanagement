import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config import Config

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_jwt(payload):
    payload['exp'] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
