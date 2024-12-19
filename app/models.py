from app import db
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

# 用户与服务器的关联表（多对多关系）
user_server_association = db.Table(
    'user_server_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True),
    db.UniqueConstraint('user_id', 'server_id', name='uq_user_server')  # 定义唯一约束
)

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rental_expiry = db.Column(db.DateTime, nullable=True)  # 租赁到期时间
    created_at = db.Column(db.DateTime, default=func.now())  # 用户创建时间
    serial_numbers = db.relationship('SerialNumber', backref='user', lazy='dynamic')  # 序列号绑定
    servers = relationship('Server', secondary=user_server_association, back_populates='users')  # 用户绑定服务器
    containers = relationship('UserContainer', back_populates='user')  # 容器关联

    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError("Invalid email address")
        return address

# 序列号模型
class SerialNumber(db.Model):
    __tablename__ = 'serial_numbers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)  # 序列号代码
    duration_days = db.Column(db.Integer, nullable=False)  # 有效时长（天）
    status = db.Column(db.String(50), default='unused')  # 状态（unused, used）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 绑定用户
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    used_at = db.Column(db.DateTime, nullable=True, onupdate=func.now())  # 使用时间

# 服务器模型
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间
    users = relationship('User', secondary=user_server_association, back_populates='servers')  # 用户绑定
    containers = relationship('UserContainer', back_populates='server')  # 容器关联

# 用户容器模型
class UserContainer(db.Model):
    __tablename__ = 'user_containers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户 ID
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)  # 服务器 ID
    port = db.Column(db.Integer, nullable=False)  # DERP 端口
    stun_port = db.Column(db.Integer, nullable=False)  # STUN 端口
    upload_traffic = db.Column(db.Float, default=0.0)  # 上传流量
    download_traffic = db.Column(db.Float, default=0.0)  # 下载流量
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    user = relationship('User', back_populates='containers')  # 反向关联用户
    server = relationship('Server', back_populates='containers')  # 反向关联服务器
