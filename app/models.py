from app import db 
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import timedelta
from datetime import datetime
import re

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
    role = db.Column(db.Enum('user', 'admin', 'distributor', name='role_enum'), default='user')  # 改为枚举类型
    rental_expiry = db.Column(db.DateTime, nullable=True)  # 租赁到期时间
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间
    serial_numbers = relationship('SerialNumber', backref='user', lazy='dynamic')  # 序列号绑定
    servers = relationship('Server', secondary=user_server_association, back_populates='users')  # 用户绑定服务器
    containers = relationship('UserContainer', back_populates='user')  # 容器关联
    logs = relationship('UserLog', back_populates='user', lazy='dynamic')  # 用户日志关联
    histories = relationship('UserHistory', backref='user', lazy='dynamic')  # 用户历史记录

    # 新增字段
    is_banned = db.Column(db.Boolean, default=False)
    banned_reason = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    password_encrypted = db.Column(db.Boolean, default=True)

    @validates('email')
    def validate_email(self, key, address):
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, address):
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
    expires_at = db.Column(db.DateTime, nullable=False)  # 序列号过期时间（新增字段）

    def update_user_rental_expiry(self):
        if self.status == 'used' and self.user:
            self.user.rental_expiry = self.used_at + timedelta(days=self.duration_days)
            db.session.commit()


# 服务器模型
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区
    status = db.Column(db.String(50), default='healthy')  # 服务器状态（healthy, unhealthy）
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间
    users = relationship('User', secondary=user_server_association, back_populates='servers')  # 用户绑定
    containers = relationship('UserContainer', back_populates='server')  # 容器关联
    logs = relationship('ServerLog', back_populates='server', lazy='dynamic')  # 服务器日志关联
    total_traffic = db.Column(db.Float, nullable=False, default=1000.0)  # 总流量（GB）
    remaining_traffic = db.Column(db.Float, nullable=False, default=1000.0)  # 剩余流量（GB）

    def __repr__(self):
        return f"<Server {self.ip}>"


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

    def check_traffic_limit(self, upload_limit, download_limit):
        if self.upload_traffic > upload_limit or self.download_traffic > download_limit:
            # 触发流量限制
            return True
        return False


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

# 监控日志模型（更新）
class MonitoringLog(db.Model):
    __tablename__ = 'monitoring_logs'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=True)  # 关联的服务器
    is_reachable = db.Column(db.Boolean, nullable=False)  # 服务器是否可用
    ping_latency = db.Column(db.Float, nullable=False)  # Ping 时延（毫秒）
    total_traffic = db.Column(db.Float, nullable=False)  # 总流量（MB）
    download_traffic = db.Column(db.Float, nullable=False)  # 下载流量（MB）
    upload_traffic = db.Column(db.Float, nullable=False)  # 上传流量（MB）
    timestamp = db.Column(db.DateTime, default=func.now())  # 时间戳
    server = relationship('Server', backref='monitoring_logs')  # 关联服务器

# 系统告警模型（更新）
class SystemAlert(db.Model):
    __tablename__ = 'system_alerts'
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 告警类型
    severity = db.Column(db.Enum('low', 'medium', 'high'), default='low')  # 告警严重性
    message = db.Column(db.Text, nullable=False)  # 告警消息
    resolved = db.Column(db.Boolean, default=False)  # 是否已解决
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间
    resolved_at = db.Column(db.DateTime, nullable=True)  # 解决时间（新增字段）

# 设备与服务器之间的 ACL 配置模型
class ACLConfig(db.Model):
    __tablename__ = 'acl_configs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户
    user = db.relationship('User', backref=db.backref('acl_configs', lazy=True))
    
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)  # 关联服务器
    server = db.relationship('Server', backref=db.backref('acl_configs', lazy=True))

    container_id = db.Column(db.Integer, db.ForeignKey('user_containers.id'), nullable=False)  # 关联容器
    container = db.relationship('UserContainer', backref=db.backref('acl_configs', lazy=True))
    
    derp_port = db.Column(db.Integer, nullable=False)  # DERP 服务的端口号
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    def __repr__(self):
        return f"<ACLConfig user_id={self.user_id} server_id={self.server_id} container_id={self.container_id}>"

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    subject = db.Column(db.String(255), nullable=False)  # 邮件主题
    body = db.Column(db.Text, nullable=False)  # 邮件内容
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)  # 发送时间
    status = db.Column(db.String(20), nullable=False)  # 发送状态：成功或失败
    error_message = db.Column(db.String(255), nullable=True)  # 错误信息（如果有）

    def __repr__(self):
        return f"<NotificationLog {self.id} - {self.status}>"
from app import db
from datetime import datetime

# 用户模型
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'admin', 'distributor', name='role_enum'), default='user')
    rental_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_banned = db.Column(db.Boolean, default=False)
    banned_reason = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    password_encrypted = db.Column(db.Boolean, default=True)

    logs = db.relationship('UserLog', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

# 用户日志模型
class UserLog(db.Model):
    __tablename__ = 'user_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operation = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(255), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<UserLog {self.operation}>"

# 角色权限模型
class RolePermission(db.Model):
    __tablename__ = 'roles_permissions'

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), unique=True, nullable=False)
    permissions = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<RolePermission {self.role_name}>"

# 分销员佣金模型
class DistributorCommission(db.Model):
    __tablename__ = 'distributor_commission'

    id = db.Column(db.Integer, primary_key=True)
    distributor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    serial_number = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'paid', name='commission_status'), default='pending')

    distributor = db.relationship('User', backref='commissions')

    def __repr__(self):
        return f"<DistributorCommission {self.serial_number}, {self.amount}>"

# 租赁信息模型
class Rental(db.Model):
    __tablename__ = 'rentals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('active', 'expired', 'paused', name='rental_status'), default='active')
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    server_ids = db.Column(db.JSON, nullable=True)
    container_ids = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref='rentals')

    def __repr__(self):
        return f"<Rental {self.user_id}, {self.status}>"

# 续费通知模型
class RenewalNotification(db.Model):
    __tablename__ = 'renewal_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.Enum('7_days', '3_days', '1_day', name='notification_type'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    notification_channel = db.Column(db.Enum('email', 'sms', 'push', name='notification_channel'), nullable=False)
    notification_sent = db.Column(db.Boolean, default=False)
    notification_status = db.Column(db.Enum('pending', 'sent', 'failed', name='notification_status'), default='pending')
    notification_content = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref='renewal_notifications')

    def __repr__(self):
        return f"<RenewalNotification {self.user_id}, {self.notification_type}>"

# 分销员模型
class Distributor(db.Model):
    __tablename__ = 'distributors'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.Enum('distributor', 'golden_distributor', 'platinum_distributor', name='distributor_role'), nullable=False)
    commission_rate = db.Column(db.Numeric(5, 2), nullable=False)
    distributor_mode = db.Column(db.Enum('mode1', 'mode2', name='distributor_mode'), nullable=False)
    unique_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Distributor {self.username}, {self.role}>"

# 序列号模型
class SerialNumber(db.Model):
    __tablename__ = 'serial_numbers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.Enum('unused', 'used', 'expired', name='serial_status'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    valid_days = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    activated_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    distributor_id = db.Column(db.Integer, db.ForeignKey('distributors.id'), nullable=True)
    payment_status = db.Column(db.Enum('paid', 'unpaid', name='payment_status'), default='unpaid')

    user = db.relationship('User', backref='serial_numbers')
    distributor = db.relationship('Distributor', backref='serial_numbers')

    def __repr__(self):
        return f"<SerialNumber {self.code}, {self.status}>"

# 服务器分类模型
class ServerCategory(db.Model):
    __tablename__ = 'server_categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ServerCategory {self.category_name}>"
