import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """
    应用配置类，加载 .env 文件中的变量，同时提供默认值。
    """
    # 应用安全密钥
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # 生产环境中确保设置强密码

    # 数据库配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 生产环境中，可以将数据库切换为 PostgreSQL 或 MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "app.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭对象修改追踪

    # 邮件服务器配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_password')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ['true', '1']

    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    # Celery 配置
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 默认日志级别为 INFO
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')  # 日志文件路径

    # JWT 配置
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))  # 默认24小时

    # 其他配置项（如缓存、API配置等）可以继续在这里添加...
