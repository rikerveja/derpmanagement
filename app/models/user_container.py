from app import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class UserContainer(db.Model):
    __tablename__ = 'user_containers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    port = db.Column(db.Integer, nullable=False)  # DERP 端口
    stun_port = db.Column(db.Integer, nullable=False)  # STUN 端口
    created_at = db.Column(db.DateTime, default=func.now())
    user = relationship('User', back_populates='containers')
    server = relationship('Server', back_populates='containers')