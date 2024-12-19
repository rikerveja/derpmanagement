from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from app.config import Config
import logging
from logging.handlers import RotatingFileHandler

# 初始化插件
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

def setup_logging(app):
    """设置日志记录"""
    handler = RotatingFileHandler("app.log", maxBytes=100000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 设置日志
    setup_logging(app)

    try:
        # 初始化插件
        db.init_app(app)
        mail.init_app(app)
        migrate.init_app(app, db)
    except Exception as e:
        app.logger.error(f"Initialization error: {e}")
        raise

    # 注册蓝图
    from app.routes.user_routes import user_bp
    from app.routes.server_routes import server_bp
    from app.routes.container_routes import container_bp
    from app.routes.acl_routes import acl_bp
    from app.routes.finance_routes import finance_bp
    from app.routes.rental_routes import rental_bp  # 新增租赁管理模块
    from app.routes.logs_routes import logs_bp  # 新增日志与审计模块
    from app.routes.ha_routes import ha_bp  # 新增高可用模块
    from app.routes.notifications_routes import notifications_bp  # 新增通知模块

    app.register_blueprint(user_bp)
    app.register_blueprint(server_bp)
    app.register_blueprint(container_bp)
    app.register_blueprint(acl_bp, url_prefix='/api/acl')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')
    app.register_blueprint(rental_bp, url_prefix='/api/rental')  # 注册租赁蓝图
    app.register_blueprint(logs_bp, url_prefix='/api/logs')  # 注册日志蓝图
    app.register_blueprint(ha_bp, url_prefix='/api/ha')  # 注册高可用蓝图
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')  # 注册通知蓝图

    app.logger.info("App successfully created and initialized.")
    return app
