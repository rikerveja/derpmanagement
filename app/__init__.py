
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from app.config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)  # 确保 Flask-Mail 正确初始化
    return app


    from app.routes.user_routes import user_bp
    from app.routes.server_routes import server_bp
    from app.routes.container_routes import container_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(server_bp)
    app.register_blueprint(container_bp)

    return app
