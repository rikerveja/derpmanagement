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
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的根目录路径

    # 如果使用 MySQL 数据库，支持从环境变量中加载数据库 URL
    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    else:
        # 默认使用 SQLite 数据库
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'
    
    # 禁用对象修改追踪，提升性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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

    # Celery 配置（如果需要使用 Celery 进行异步任务处理）
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

    # 日志级别配置（根据需求进行动态调整）
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 默认日志级别为 INFO
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')  # 可以在 .env 文件中指定日志文件路径

    # JWT 配置
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))  # 默认设置为24小时

    # 监控配置
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 60))  # 监控日志收集时间间隔（秒）
    ALERT_THRESHOLD = float(os.getenv('ALERT_THRESHOLD', 0.5))  # 告警阈值：Ping 时延（毫秒）

    # 流量监控配置
    TRAFFIC_MONITORING_INTERVAL = int(os.getenv('TRAFFIC_MONITORING_INTERVAL', 3600))  # 流量统计更新间隔（秒）
    MAX_UPLOAD_TRAFFIC = int(os.getenv('MAX_UPLOAD_TRAFFIC', 1000))  # 最大上传流量（MB）
    MAX_DOWNLOAD_TRAFFIC = int(os.getenv('MAX_DOWNLOAD_TRAFFIC', 1000))  # 最大下载流量（MB）

    # 配置 MySQL 默认字符集，确保支持 emoji 和特殊字符
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"charset": "utf8mb4"},
    }

    # 其他自定义配置（如日志、缓存等）可以在此处添加

    # 安全与设备绑定配置（如有设备管理）
    SECURITY_KEY = os.getenv('SECURITY_KEY', 'default_security_key')
    DEVICE_BINDING_ENABLED = os.getenv('DEVICE_BINDING_ENABLED', 'False').lower() in ['true', '1']
