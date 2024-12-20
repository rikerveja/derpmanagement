from app import db
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import timedelta

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
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 用户角色（user, admin）
    rental_expiry = db.Column(db.DateTime, nullable=True)  # 租赁到期时间
    created_at = db.Column(db.DateTime, default=func.now())  # 用户创建时间
    serial_numbers = db.relationship('SerialNumber', backref='user', lazy='dynamic')  # 序列号绑定
    servers = relationship('Server', secondary=user_server_association, back_populates='users')  # 用户绑定服务器
    containers = relationship('UserContainer', back_populates='user')  # 容器关联
    logs = relationship('UserLog', back_populates='user', lazy='dynamic')  # 用户日志关联
    histories = relationship('UserHistory', backref='user', lazy='dynamic')  # 用户历史记录

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
    status = db.Column(db.String(50), default='unused')  # 状态（unused, used, expired）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 绑定用户
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    used_at = db.Column(db.DateTime, nullable=True, onupdate=func.now())  # 使用时间

    def update_user_rental_expiry(self):
        if self.status == 'active' and self.user:
            self.user.rental_expiry = self.used_at + timedelta(days=self.duration_days)
            db.session.commit()


# 服务器模型
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    status = db.Column(db.String(50), default='healthy')  # 服务器状态（healthy, unhealthy）
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间
    users = relationship('User', secondary=user_server_association, back_populates='servers')  # 用户绑定
    containers = relationship('UserContainer', back_populates='server')  # 容器关联
    logs = relationship('ServerLog', back_populates='server', lazy='dynamic')  # 服务器日志关联


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

    def update_traffic(self, upload, download):
        self.upload_traffic += upload
        self.download_traffic += download
        db.session.commit()


# 用户日志模型
class UserLog(db.Model):
    __tablename__ = 'user_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户 ID
    action = db.Column(db.String(255), nullable=False)  # 操作描述
    timestamp = db.Column(db.DateTime, default=func.now())  # 操作时间
    user = relationship('User', back_populates='logs')  # 反向关联用户


# 服务器日志模型
class ServerLog(db.Model):
    __tablename__ = 'server_logs'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)  # 服务器 ID
    event = db.Column(db.String(255), nullable=False)  # 事件描述
    timestamp = db.Column(db.DateTime, default=func.now())  # 事件时间
    server = relationship('Server', back_populates='logs')  # 反向关联服务器


# 用户历史记录模型
class UserHistory(db.Model):
    __tablename__ = 'user_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户 ID
    rental_start = db.Column(db.DateTime, nullable=False)  # 租赁开始时间
    rental_end = db.Column(db.DateTime, nullable=False)  # 租赁结束时间
    total_traffic = db.Column(db.Float, default=0.0)  # 总流量
    created_at = db.Column(db.DateTime, default=func.now())  # 记录时间


# ACL 日志记录模型
class ACLLog(db.Model):
    __tablename__ = 'acl_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 用户 ID
    ip_address = db.Column(db.String(50), nullable=False)  # 用户 IP 地址
    location = db.Column(db.String(255), nullable=True)  # 地理位置
    acl_version = db.Column(db.String(50), nullable=False)  # ACL 版本号
    created_at = db.Column(db.DateTime, default=func.now())  # 生成时间


# 系统日志模型
class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # 操作者的用户 ID，可为空
    operation = db.Column(db.String(255), nullable=False)  # 操作名称
    status = db.Column(db.String(50), nullable=False)  # 操作状态（如 success, failed）
    ip_address = db.Column(db.String(50), nullable=True)  # 操作者的 IP 地址
    details = db.Column(db.Text, nullable=True)  # 操作的详细信息
    timestamp = db.Column(db.DateTime, default=func.now())  # 操作时间


from app import db
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import timedelta

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
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 用户角色（user, admin）
    rental_expiry = db.Column(db.DateTime, nullable=True)  # 租赁到期时间
    created_at = db.Column(db.DateTime, default=func.now())  # 用户创建时间
    serial_numbers = db.relationship('SerialNumber', backref='user', lazy='dynamic')  # 序列号绑定
    servers = relationship('Server', secondary=user_server_association, back_populates='users')  # 用户绑定服务器
    containers = relationship('UserContainer', back_populates='user')  # 容器关联
    logs = relationship('UserLog', back_populates='user', lazy='dynamic')  # 用户日志关联
    histories = relationship('UserHistory', backref='user', lazy='dynamic')  # 用户历史记录

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
    status = db.Column(db.String(50), default='unused')  # 状态（unused, used, expired）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 绑定用户
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    used_at = db.Column(db.DateTime, nullable=True, onupdate=func.now())  # 使用时间

    def update_user_rental_expiry(self):
        if self.status == 'active' and self.user:
            self.user.rental_expiry = self.used_at + timedelta(days=self.duration_days)
            db.session.commit()


# 服务器模型
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    status = db.Column(db.String(50), default='healthy')  # 服务器状态（healthy, unhealthy）
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间
    users = relationship('User', secondary=user_server_association, back_populates='servers')  # 用户绑定
    containers = relationship('UserContainer', back_populates='server')  # 容器关联
    logs = relationship('ServerLog', back_populates='server', lazy='dynamic')  # 服务器日志关联


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

    def update_traffic(self, upload, download):
        self.upload_traffic += upload
        self.download_traffic += download
        db.session.commit()


# 系统日志模型
class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # 操作者的用户 ID，可为空
    operation = db.Column(db.String(255), nullable=False)  # 操作名称
    status = db.Column(db.String(50), nullable=False)  # 操作状态（如 success, failed）
    ip_address = db.Column(db.String(50), nullable=True)  # 操作者的 IP 地址
    details = db.Column(db.Text, nullable=True)  # 操作的详细信息
    timestamp = db.Column(db.DateTime, default=func.now())  # 操作时间


# 监控日志模型
class MonitoringLog(db.Model):
    __tablename__ = 'monitoring_logs'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=True)  # 关联的服务器
    metric = db.Column(db.String(255), nullable=False)  # 监控指标名称
    value = db.Column(db.Float, nullable=False)  # 监控值
    timestamp = db.Column(db.DateTime, default=func.now())  # 时间戳
    server = relationship('Server', backref='monitoring_logs')  # 关联服务器


# 系统告警模型
class SystemAlert(db.Model):
    __tablename__ = 'system_alerts'
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 告警类型
    severity = db.Column(db.String(20), nullable=False)  # 严重程度（info, warning, critical）
    message = db.Column(db.String(255), nullable=False)  # 告警信息
    timestamp = db.Column(db.DateTime, default=func.now())  # 时间戳
    resolved = db.Column(db.Boolean, default=False)  # 是否已解决
