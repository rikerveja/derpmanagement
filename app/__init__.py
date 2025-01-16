# app/__init__.py

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from celery import Celery
from app.config import Config
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化插件
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
celery = None


def setup_logging(app):
    """设置日志记录"""
    log_file = app.config['LOG_FILE']
    handler = RotatingFileHandler(log_file, maxBytes=100000000, backupCount=3)
    handler.setLevel(logging.INFO)  # 设置日志级别
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)


def make_celery(app):
    """
    初始化 Celery
    """
    celery_instance = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery_instance.conf.update(app.config)
    return celery_instance


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置日志
    setup_logging(app)

    # 设置 FLASK_APP 环境变量
    if not os.getenv("FLASK_APP"):
        os.environ["FLASK_APP"] = "app"

    try:
        # 初始化插件
        db.init_app(app)
        mail.init_app(app)
        migrate.init_app(app, db)

        # 初始化 Celery
        global celery
        celery = make_celery(app)

    except Exception as e:
        app.logger.error(f"Initialization error: {e}")
        raise

    # 注册蓝图
    from app.routes.user_routes import user_bp
    from app.routes.server_routes import server_bp
    from app.routes.container_routes import container_bp
    from app.routes.acl_routes import acl_bp
    from app.routes.finance_routes import finance_bp
    from app.routes.rental_routes import rental_bp
    from app.routes.logs_routes import logs_bp
    from app.routes.ha_routes import ha_bp
    from app.routes.notifications_routes import notifications_bp
    from app.routes.admin_routes import admin_bp  # 管理员模块
    from app.routes.traffic_routes import traffic_bp  # 流量模块
    from app.routes.alerts_routes import alerts_bp  # 告警模块
    from app.routes.monitoring_routes import monitoring_bp  # 新增：监控模块
    from app.routes.serial_routes import serial_bp  # 新增：序列号管理模块
    from app.routes.security_routes import security_bp  # 新增：安全与设备绑定模块
    from app.utils.user_history import user_history_bp  # 从 utils 导入 user_history 蓝图

    # 新增：注册 system_bp 蓝图
    from app.routes.system import system_bp  # 导入 system_bp 蓝图
    app.register_blueprint(system_bp, url_prefix='')  # 注册 system_bp 蓝图

    # 蓝图注册到 Flask 应用
    app.register_blueprint(user_bp, url_prefix='')
    app.register_blueprint(server_bp, url_prefix='')
    app.register_blueprint(container_bp, url_prefix='')
    app.register_blueprint(acl_bp, url_prefix='')
    app.register_blueprint(finance_bp, url_prefix='')
    app.register_blueprint(rental_bp, url_prefix='')
    app.register_blueprint(logs_bp, url_prefix='')
    app.register_blueprint(ha_bp, url_prefix='')
    app.register_blueprint(notifications_bp, url_prefix='')
    app.register_blueprint(admin_bp, url_prefix='')  # 管理员模块
    app.register_blueprint(traffic_bp, url_prefix='')  # 流量模块
    app.register_blueprint(alerts_bp, url_prefix='')  # 告警模块
    app.register_blueprint(monitoring_bp, url_prefix='')  # 新增：监控模块
    app.register_blueprint(serial_bp, url_prefix='')  # 新增：序列号管理模块
    app.register_blueprint(security_bp, url_prefix='')  # 新增：安全与设备绑定模块
    app.register_blueprint(user_history_bp, url_prefix='')  # 注册 user_history 蓝图

    app.logger.info("App successfully created and initialized.")
    return app


# 此部分应放在 create_app() 函数外部，确保 Flask 应用实例 `app` 已初始化
app = create_app()  # 创建应用实例

@app.route('/api/urls', methods=['GET'])
def get_api_urls():
    api_urls = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static' and '/api/' in str(rule):
            methods = ', '.join(rule.methods)  # 获取该路由支持的 HTTP 方法
            api_urls.append({
                'endpoint': rule.endpoint,  # 路由的 endpoint 名称
                'url': str(rule),            # 路由的完整 URL
                'methods': methods           # 路由支持的 HTTP 方法
            })
    return jsonify(api_urls)
