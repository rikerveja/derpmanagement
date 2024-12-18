from app import db
from sqlalchemy.sql import func

class SerialNumber(db.Model):
    __tablename__ = 'serial_numbers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='unused')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    used_at = db.Column(db.DateTime, nullable=True, onupdate=func.now())