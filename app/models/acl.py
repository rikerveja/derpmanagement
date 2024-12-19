# app/models/acl.py
from app import db
from sqlalchemy.sql import func

class ACLConfig(db.Model):
    __tablename__ = 'acl_configs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    config_data = db.Column(db.Text, nullable=False)  # 存储 ACL 文件内容
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)  # ACL 有效期
    user = db.relationship('User', backref='acl_configs')
    server = db.relationship('Server', backref='acl_configs')
