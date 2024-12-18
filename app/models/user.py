from app import db
from app.models.associations import user_server_association
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    serial_numbers = db.relationship('SerialNumber', backref='user', lazy='dynamic')
    servers = relationship('Server', secondary=user_server_association, back_populates='users')
    containers = relationship('UserContainer', back_populates='user')  # 容器关联

    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError("Invalid email address")
        return address