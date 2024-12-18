from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from app.config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化 Flask 插件
    db.init_app(app)
    mail.init_app(app)

    # 自动生成数据库表
    with app.app_context():
        db.create_all()  # 创建所有数据库表

    # 注册蓝图
    from app.routes.user_routes import user_bp
    from app.routes.server_routes import server_bp
    from app.routes.container_routes import container_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(server_bp)
    app.register_blueprint(container_bp)

    return app
