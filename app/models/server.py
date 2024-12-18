from app import db
from app.models.associations import user_server_association
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    users = relationship('User', secondary=user_server_association, back_populates='servers')
    containers = relationship('UserContainer', back_populates='server')  # 容器关联