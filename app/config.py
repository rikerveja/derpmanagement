import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """
    应用配置类，加载 .env 文件中的变量，同时提供默认值。
    """
    # 应用安全密钥
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用追踪修改以提高性能

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

    # 日志级别（可选）
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 默认日志级别为 INFO

    # JWT 配置
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
