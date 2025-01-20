from app import db 
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy import Text
from datetime import timedelta
from datetime import datetime
import re
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, DECIMAL, JSON, UniqueConstraint, ForeignKeyConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 用户与服务器的关联表（多对多关系）
user_server_association = db.Table(
    'user_server_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True),
    db.UniqueConstraint('user_id', 'server_id', name='uq_user_server')  # 定义唯一约束
)

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum('user', 'admin', 'distributor', name='user_roles'), default='user', nullable=False)
    rental_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_banned = Column(Boolean, default=False)
    banned_reason = Column(String(255))
    last_login = Column(DateTime)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    password_encrypted = Column(Boolean, default=True)

    logs = relationship("UserLog", back_populates="user")
    commissions = relationship("DistributorCommission", back_populates="distributor")
    rentals = relationship("Rental", back_populates="user")
    serial_numbers = relationship("SerialNumber", back_populates="user")
    notifications = relationship("RenewalNotification", back_populates="user")  # 这里定义了与 RenewalNotification 的关系
    operation_logs = relationship("OperationLog", back_populates="user")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_role', 'role'),
    )


class UserLog(db.Model):
    __tablename__ = 'user_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    operation = Column(String(255))
    details = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(255))
    user_agent = Column(String(255))

    user = relationship("User", back_populates="logs")


class RolePermission(db.Model):
    __tablename__ = 'roles_permissions'

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), unique=True, nullable=False)
    permissions = Column(String(1024))


class DistributorCommission(db.Model):
    __tablename__ = 'distributor_commissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    commission_amount = Column(DECIMAL(10, 2))
    status = Column(Enum('pending', 'paid', name='commission_status'), default='pending')
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    distributor = relationship("User", back_populates="commissions")
    invoice = relationship("Invoice")

    __table_args__ = (
        Index('idx_commission_distributor', 'distributor_id'),
        Index('idx_commission_status', 'status'),
    )


class Rental(db.Model):
    __tablename__ = 'rentals'
    
    # 已有字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    status = db.Column(db.Enum('active', 'pending', 'expired', 'suspended', 'terminated', 'canceled'), default='active', nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    expired_at = db.Column(db.DateTime)  # 到期时间
    server_ids = db.Column(db.JSON, default=dict)  # 服务器ID列表
    container_ids = db.Column(db.JSON, default=dict)  # 容器ID列表
    traffic_limit = db.Column(db.Integer, default=0)  # 流量限制
    traffic_usage = db.Column(db.Integer, default=0)  # 已使用流量
    traffic_reset_date = db.Column(db.Date)  # 流量重置日期
    serial_number_id = db.Column(db.Integer, db.ForeignKey('serial_numbers.id'))
    serial_number_expiry = db.Column(db.Date)  # 序列号有效期
    renewed_at = db.Column(db.Date)  # 续费日期
    renewal_count = db.Column(db.Integer, default=0)  # 续费次数
    container_status = db.Column(db.Enum('active', 'inactive', 'terminated'), default='active')  # 容器状态
    server_status = db.Column(db.Enum('active', 'inactive', 'failed'), default='active')  # 服务器状态
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')  # 支付状态
    payment_date = db.Column(db.DateTime)  # 支付日期
    tenant_id = db.Column(db.Integer)  # 租户ID
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", back_populates="rentals")

class RenewalNotification(db.Model):
    __tablename__ = 'renewal_notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id', ondelete='CASCADE'))
    renewal_amount = Column(DECIMAL(10, 2))
    renewal_period = Column(Integer)
    renewal_date = Column(DateTime, nullable=False)
    renewal_status = Column(Enum('paid', 'pending', 'failed'), default='pending')
    sent_at = Column(DateTime)
    notification_type = Column(Enum('first', 'last', 'success'), default='first')
    notification_channel = Column(Enum('email', 'sms', 'push'), default='email')
    notification_sent = Column(Boolean, default=False)
    notification_status = Column(Enum('sent', 'failed'), default='sent')
    notification_content = Column(String(1024))

    user = relationship("User", back_populates="notifications")  # 反向关系
    serial_number = relationship("SerialNumber", back_populates="renewal_notifications")

    __table_args__ = (
        Index('idx_renewal_notification_user', 'user_id'),
        Index('idx_renewal_notification_status', 'renewal_status'),
    )


class Distributor(db.Model):
    __tablename__ = 'distributors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(Enum('distributor', 'golden_distributor', 'platinum_distributor', name='distributor_roles'), nullable=False)
    commission_rate = Column(DECIMAL(5, 2), nullable=False)
    distributor_mode = Column(Enum('mode1', 'mode2', name='distributor_modes'), nullable=False)
    unique_link = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    serial_numbers = relationship("SerialNumber", back_populates="distributor")

    __table_args__ = (
        UniqueConstraint('email', name='unique_distributor_email'),
        Index('idx_distributor_username', 'username'),
        Index('idx_distributor_role', 'role'),
        Index('idx_distributor_mode', 'distributor_mode'),
    )


class SerialNumber(db.Model):
    __tablename__ = 'serial_numbers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), unique=True, nullable=False)
    status = Column(Enum('unused', 'used', 'expired', name='serial_number_status'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    valid_days = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    activated_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    used_at = Column(DateTime)
    distributor_id = Column(Integer, ForeignKey('distributors.id', ondelete='SET NULL'))
    payment_status = Column(Enum('paid', 'unpaid', name='payment_status'), default='unpaid')

    user = relationship("User", back_populates="serial_numbers")
    renewal_notifications = relationship("RenewalNotification", back_populates="serial_number")
    distributor = relationship("Distributor", back_populates="serial_numbers")

    __table_args__ = (
        Index('idx_serial_code', 'code'),
        Index('idx_serial_status', 'status'),
        Index('idx_serial_user', 'user_id'),
    )


class SerialUserAssociation(db.Model):
    __tablename__ = 'serial_user_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id', ondelete='CASCADE'))
    status = Column(Enum('activated', 'pending', 'expired', name='serial_status'), default='pending')
    activated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    serial_number = relationship("SerialNumber")


class ServerCategory(db.Model):
    __tablename__ = 'server_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255), nullable=False)


class Server(db.Model):
    __tablename__ = 'servers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_name = Column(String(255), nullable=False)
    ip_address = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey('server_categories.id', ondelete='SET NULL'))
    cpu = Column(String(50))
    memory = Column(String(50))
    storage = Column(String(50))
    bandwidth = Column(String(255))
    status = Column(Enum('healthy', 'unhealthy', 'maintenance', name='server_status'), default='healthy', nullable=False)
    server_type = Column(String(255))
    region = Column(String(255))
    user_count = Column(Integer, default=0)
    total_traffic = Column(DECIMAL(10, 2))
    remaining_traffic = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("ServerCategory")

    __table_args__ = (
        Index('idx_server_status', 'status'),
        Index('idx_server_region', 'region'),
    )

class DockerContainer(db.Model):
    __tablename__ = 'docker_containers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String(255), unique=True, nullable=False)
    container_name = Column(String(255), nullable=False)  # 新增字段: container_name
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    port = Column(Integer)
    stun_port = Column(Integer)
    node_exporter_port = Column(Integer)  # 新增字段: node_exporter_port
    status = Column(Enum('running', 'stopped', 'paused', 'restarting', 'exited', name='container_status'), default='running', nullable=False)
    image = Column(String(255))
    max_upload_traffic = Column(DECIMAL(10, 2))
    max_download_traffic = Column(DECIMAL(10, 2))
    upload_traffic = Column(DECIMAL(10, 2))
    download_traffic = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    server = relationship("Server")
    user = relationship("User")

    __table_args__ = (
        Index('idx_container_status', 'status'),
        Index('idx_container_server', 'server_id'),
        Index('idx_container_user', 'user_id'),
    )

class SerialServerAssociation(db.Model):
    __tablename__ = 'serial_server_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id', ondelete='CASCADE'))
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    serial_number = relationship("SerialNumber")
    server = relationship("Server")
    container = relationship("DockerContainer")


class SerialHistory(db.Model):
    __tablename__ = 'serial_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    operation = Column(Enum('generated', 'activated', 'expired', name='serial_history_status'), nullable=False)
    details = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    serial_number = relationship("SerialNumber")


class ServerContainerAssociation(db.Model):
    __tablename__ = 'server_container_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    server = relationship("Server")
    container = relationship("DockerContainer")


class ServerHistory(db.Model):
    __tablename__ = 'server_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    operation = Column(Enum('status_change', 'maintenance', 'downtime', 'restore', name='server_operation'))
    details = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")


class ServerTrafficMonitoring(db.Model):
    __tablename__ = 'server_traffic_monitoring'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    total_traffic = Column(DECIMAL(10, 2))
    used_traffic = Column(DECIMAL(10, 2))
    remaining_traffic = Column(DECIMAL(10, 2))
    timestamp = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")

    __table_args__ = (
        Index('idx_traffic_server', 'server_id'),
        Index('idx_traffic_timestamp', 'timestamp'),
    )


class ServerPerformanceMonitoring(db.Model):
    __tablename__ = 'server_performance_monitoring'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    cpu_usage = Column(DECIMAL(10, 2))
    memory_usage = Column(DECIMAL(10, 2))
    network_latency = Column(DECIMAL(10, 2))
    timestamp = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")

    __table_args__ = (
        Index('idx_perf_server', 'server_id'),
        Index('idx_perf_timestamp', 'timestamp'),
    )


class DockerContainerResources(db.Model):
    __tablename__ = 'docker_container_resources'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'))
    cpu_limit = Column(DECIMAL(10, 2))
    memory_limit = Column(DECIMAL(10, 2))
    disk_limit = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    container = relationship("DockerContainer")


class DockerContainerTraffic(db.Model):
    __tablename__ = 'docker_container_traffic'
    
    # 已有字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_id = db.Column(db.Integer, db.ForeignKey('docker_containers.id'))
    upload_traffic = db.Column(db.DECIMAL(10, 2))  # 上传流量
    download_traffic = db.Column(db.DECIMAL(10, 2))  # 下载流量
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # 流量记录时间
    traffic_limit = db.Column(db.DECIMAL(10, 2))  # 流量限制
    remaining_traffic = db.Column(db.DECIMAL(10, 2))  # 剩余流量
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    container = db.relationship("DockerContainer")
    

class DockerContainerEvents(db.Model):
    __tablename__ = 'docker_container_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'))
    event_type = Column(Enum('start', 'stop', 'restart', 'pause', 'unpause', 'error', name='container_event_type'))
    event_message = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")


class DockerContainerLogs(db.Model):
    __tablename__ = 'docker_container_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'))
    log_level = Column(Enum('info', 'warn', 'error', name='log_level'))
    log_message = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")


class ACLConfig(db.Model):
    __tablename__ = 'acl_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    server_ids = Column(JSON, default=dict)
    container_ids = Column(JSON, default=dict)
    acl_data = Column(JSON, default=dict)
    version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User")

    __table_args__ = (
        Index('idx_acl_user', 'user_id'),
        Index('idx_acl_active', 'is_active'),
    )


class ACLVerificationLog(db.Model):
    __tablename__ = 'acl_verification_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    acl_id = Column(Integer, ForeignKey('acl_configs.id', ondelete='CASCADE'))
    ip_address = Column(String(50))
    location = Column(String(255))
    status = Column(Enum('approved', 'denied', name='verification_status'), default='pending', nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    acl_config = relationship("ACLConfig")


class ACLLog(db.Model):
    __tablename__ = 'acl_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    operation = Column(Enum('generate', 'update', 'delete', name='acl_operation'))
    acl_config_id = Column(Integer, ForeignKey('acl_configs.id', ondelete='CASCADE'))
    details = Column(String(1024)) 
    ip_address = Column(String(255))
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    acl_config = relationship("ACLConfig")


class ACLFilePath(db.Model):
    __tablename__ = 'acl_file_paths'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    acl_config_id = Column(Integer, ForeignKey('acl_configs.id', ondelete='CASCADE'))
    file_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    acl_config = relationship("ACLConfig")


class ACLDownloadLog(db.Model):
    __tablename__ = 'acl_download_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    acl_file_id = Column(Integer, ForeignKey('acl_file_paths.id', ondelete='CASCADE'))
    download_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(255))

    user = relationship("User")
    acl_file = relationship("ACLFilePath")


class AlarmRule(db.Model):
    __tablename__ = 'alarm_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    alert_condition = Column(String(1024))
    threshold = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlarmLog(db.Model):
    __tablename__ = 'alarm_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey('alarm_rules.id', ondelete='SET NULL'))
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='SET NULL'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    alert_type = Column(String(255))
    message = Column(String(1024))
    status = Column(Enum('active', 'resolved', 'acknowledged', name='alarm_status'))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    rule = relationship("AlarmRule")
    server = relationship("Server")
    user = relationship("User", foreign_keys=[user_id])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index('idx_alarm_rule', 'rule_id'),
        Index('idx_alarm_server', 'server_id'),
        Index('idx_alarm_user', 'user_id'),
        Index('idx_alarm_status', 'status'),
        Index('idx_alarm_created', 'created_at'),
    )


class AlarmNotification(db.Model):
    __tablename__ = 'alarm_notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_log_id = Column(Integer, ForeignKey('alarm_logs.id', ondelete='CASCADE'))
    notification_type = Column(Enum('email', 'sms', 'push', name='notification_channel'))
    status = Column(Enum('sent', 'failed', 'pending', name='notification_status'), default='pending')
    sent_at = Column(DateTime)
    sent_to = Column(String(255))
    notification_content = Column(String(1024))

    alarm_log = relationship("AlarmLog")


class AlarmResolution(db.Model):
    __tablename__ = 'alarm_resolutions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_log_id = Column(Integer, ForeignKey('alarm_logs.id', ondelete='CASCADE'))
    action_taken = Column(String(1024))
    resolved_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    resolved_at = Column(DateTime)
    status = Column(Enum('resolved', 'ignored', 'escalated', name='resolution_status'))

    alarm_log = relationship("AlarmLog")
    resolved_by_user = relationship("User")


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(DECIMAL(10, 2))
    status = Column(Enum('pending', 'paid', 'cancelled', name='invoice_status'), default='pending')
    payment_method = Column(String(50))
    payment_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class PaymentRecord(db.Model):
    __tablename__ = 'payment_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    amount = Column(DECIMAL(10, 2))
    payment_method = Column(String(50))
    payment_time = Column(DateTime)
    status = Column(Enum('success', 'failed', 'pending', name='payment_status'), default='pending')

    user = relationship("User")
    invoice = relationship("Invoice")


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String(50), nullable=False)
    account_info = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FinanceLog(db.Model):
    __tablename__ = 'finance_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    operation = Column(String(255), nullable=False)
    details = Column(String(1024)) 
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class ContainerReplacementLog(db.Model):
    __tablename__ = 'container_replacement_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    old_container_id = Column(Integer, ForeignKey('docker_containers.id'))
    new_container_id = Column(Integer, ForeignKey('docker_containers.id'))
    status = Column(Enum('replaced', 'failed', 'in-progress', name='container_replacement_status'), nullable=False)
    reason = Column(String(1024))
    operation_type = Column(Enum('automatic', 'manual', name='operation_type'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    server = relationship("Server")
    old_container = relationship("DockerContainer", foreign_keys=[old_container_id])
    new_container = relationship("DockerContainer", foreign_keys=[new_container_id])
    user = relationship("User")


class DockerFailureLog(db.Model):
    __tablename__ = 'docker_failure_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    status = Column(Enum('failed', 'repaired', 'pending', name='docker_failure_status'), default='failed')
    repair_attempts = Column(Integer, default=0)
    last_attempt_time = Column(DateTime)
    failure_details = Column(String(1024)) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    container = relationship("DockerContainer")


class ContainerCleanupLog(db.Model):
    __tablename__ = 'container_cleanup_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    old_container_id = Column(Integer, ForeignKey('docker_containers.id'))
    cleanup_status = Column(Enum('completed', 'failed', name='cleanup_status'), nullable=False)
    cleanup_details = Column(String(1024)) 
    timestamp = Column(DateTime, default=datetime.utcnow)

    old_container = relationship("DockerContainer")


class ContainerAndServiceUpdateLog(db.Model):
    __tablename__ = 'container_and_service_update_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    service_type = Column(String(255))
    status = Column(Enum('started', 'updated', 'failed', name='update_status'), nullable=False)
    details = Column(String(1024)) 
    timestamp = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")


class UserTraffic(db.Model):
    __tablename__ = 'user_traffic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    upload_traffic = Column(DECIMAL(10, 2))
    download_traffic = Column(DECIMAL(10, 2))
    total_traffic = Column(DECIMAL(10, 2))
    traffic_limit = Column(DECIMAL(10, 2))
    remaining_traffic = Column(DECIMAL(10, 2))
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class ContainerTraffic(db.Model):
    __tablename__ = 'container_traffic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    server_id = Column(Integer, ForeignKey('servers.id'))
    upload_traffic = Column(DECIMAL(10, 2))
    download_traffic = Column(DECIMAL(10, 2))
    total_traffic = Column(DECIMAL(10, 2))
    traffic_limit = Column(DECIMAL(10, 2))
    remaining_traffic = Column(DECIMAL(10, 2))
    updated_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")
    server = relationship("Server")


class ServerTraffic(db.Model):
    __tablename__ = 'server_traffic'
    
    # 已有字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    total_traffic = db.Column(db.DECIMAL(10, 2))  # 总流量
    remaining_traffic = db.Column(db.DECIMAL(10, 2))  # 剩余流量
    traffic_limit = db.Column(db.DECIMAL(10, 2))  # 流量限制
    traffic_used = db.Column(db.DECIMAL(10, 2))  # 已使用流量
    traffic_reset_date = db.Column(db.Date)  # 流量重置日期（如每月1日重置）
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    server = db.relationship("Server")


class TrafficAlert(db.Model):
    __tablename__ = 'traffic_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_type = Column(Enum('user', 'container', 'server', name='resource_type'), nullable=False)
    resource_id = Column(Integer)
    alert_type = Column(String(255))
    threshold = Column(DECIMAL(10, 2))
    actual_traffic = Column(DECIMAL(10, 2))
    status = Column(Enum('active', 'resolved', name='alert_status'), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

    # 使用独立的外键约束
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'), nullable=True)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=True)

    # 关系定义
    user = relationship("User")
    container = relationship("DockerContainer")
    server = relationship("Server")

    __table_args__ = (
        Index('idx_traffic_alert_type', 'resource_type'),
        Index('idx_traffic_alert_status', 'status'),
    )


class TrafficReport(db.Model):
    __tablename__ = 'traffic_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_type = Column(Enum('user', 'container', 'server', name='resource_type'), nullable=False)
    resource_id = Column(Integer)
    total_traffic = Column(DECIMAL(10, 2))
    period = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 使用独立的外键约束
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'), nullable=True)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=True)

    # 关系定义
    user = relationship("User")
    container = relationship("DockerContainer")
    server = relationship("Server")

    __table_args__ = (
        Index('idx_traffic_report_type', 'resource_type'),
        Index('idx_traffic_report_period', 'period'),
    )


class DeviceBinding(db.Model):
    __tablename__ = 'device_bindings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    server_ids = Column(JSON, default=dict)
    container_ids = Column(JSON, default=dict)
    acl_id = Column(Integer, ForeignKey('acl_configs.id'))
    bind_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('active', 'inactive', name='device_binding_status'), default='active')

    user = relationship("User")
    serial_number = relationship("SerialNumber")
    acl_config = relationship("ACLConfig")

    __table_args__ = (
        Index('idx_binding_user', 'user_id'),
        Index('idx_binding_serial', 'serial_number_id'),
        Index('idx_binding_status', 'status'),
    )


class ResourceReleaseLog(db.Model):
    __tablename__ = 'resource_release_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    resource_type = Column(Enum('server', 'container', 'acl', name='resource_type'), nullable=False)
    resource_id = Column(Integer)
    release_time = Column(DateTime, default=datetime.utcnow)
    released_by = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('success', 'failed', name='release_status'), default='success')

    serial_number = relationship("SerialNumber")
    released_by_user = relationship("User")


class RenewalRecord(db.Model):
    __tablename__ = 'renewal_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    renewal_amount = Column(DECIMAL(10, 2))
    renewal_period = Column(Integer)
    renewal_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('success', 'failed', name='renewal_status'), default='success')

    user = relationship("User")
    serial_number = relationship("SerialNumber")


class DeviceValidation(db.Model):
    __tablename__ = 'device_validations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    validation_status = Column(Enum('approved', 'denied', 'pending', name='validation_status'), nullable=False)
    ip_address = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    serial_number = relationship("SerialNumber")


class DistributorSerial(db.Model):
    __tablename__ = 'distributor_serials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))
    serial_number = Column(String(255), unique=True, nullable=False)
    status = Column(Enum('unused', 'used', 'expired', name='serial_status'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    server_ids = Column(JSON, default=dict)
    container_ids = Column(JSON, default=dict)
    purchase_price = Column(DECIMAL(10, 2))
    sale_price = Column(DECIMAL(10, 2))
    commission = Column(DECIMAL(10, 2))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    distributor = relationship("Distributor")
    user = relationship("User")

    __table_args__ = (
        Index('idx_dist_serial_distributor', 'distributor_id'),
        Index('idx_dist_serial_user', 'user_id'),
        Index('idx_dist_serial_status', 'status'),
        Index('idx_dist_serial_expiry', 'expires_at'),
    )


class CommissionRecord(db.Model):
    __tablename__ = 'commission_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))
    serial_number_id = Column(Integer, ForeignKey('distributor_serials.id'))
    commission_amount = Column(DECIMAL(10, 2))
    status = Column(Enum('pending', 'paid', name='commission_status'), default='pending')
    payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    distributor = relationship("Distributor")
    serial_number = relationship("DistributorSerial")

    __table_args__ = (
        Index('idx_commission_distributor', 'distributor_id'),
        Index('idx_commission_serial', 'serial_number_id'),
        Index('idx_commission_status', 'status'),
    )


class DistributorLevel(db.Model):
    __tablename__ = 'distributor_levels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level_name = Column(String(255), nullable=False)
    commission_rate = Column(DECIMAL(5, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FinanceSettlement(db.Model):
    __tablename__ = 'finance_settlements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))
    settlement_amount = Column(DECIMAL(10, 2))
    status = Column(Enum('pending', 'paid', 'cancelled', name='settlement_status'), default='pending')
    settled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    distributor = relationship("Distributor")

    __table_args__ = (
        Index('idx_settlement_distributor', 'distributor_id'),
        Index('idx_settlement_status', 'status'),
    )


class ContainerManagementLog(db.Model):
    __tablename__ = 'container_management_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    action = Column(Enum('create', 'delete', name='container_action'), nullable=False)
    old_container_count = Column(Integer)
    new_container_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    details = Column(String(1024))

    server = relationship("Server")
    container = relationship("DockerContainer")
    user = relationship("User")


class ServerContainerCount(db.Model):
    __tablename__ = 'server_container_count'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    container_count = Column(Integer)
    max_container_limit = Column(Integer, default=10)
    last_updated = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")


class ServerContainerStatus(db.Model):
    __tablename__ = 'server_container_status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    status = Column(Enum('healthy', 'unhealthy', 'restarting', 'paused', name='container_status'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    server = relationship("Server")
    container = relationship("DockerContainer")


class SshConnectionLog(db.Model):
    __tablename__ = 'ssh_connection_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    ssh_status = Column(Enum('success', 'failed', name='ssh_status'), nullable=False)
    connect_time = Column(DateTime, default=datetime.utcnow)
    disconnect_time = Column(DateTime)
    ip_address = Column(String(255))
    details = Column(String(1024))

    operation_logs = relationship('OperationLog', back_populates='ssh_connection')


class ContainerDeploymentLog(db.Model):
    __tablename__ = 'container_deployment_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'))
    derp_service_status = Column(Enum('deployed', 'failed', name='derp_service_status'), nullable=False)
    deployment_time = Column(DateTime, default=datetime.utcnow)
    ssh_connection_id = Column(Integer, ForeignKey('ssh_connection_logs.id'))
    details = Column(String(1024))

    server = relationship("Server")
    container = relationship("DockerContainer")
    ssh_connection = relationship("SshConnectionLog")


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    target_id = Column(Integer, ForeignKey('ssh_connection_logs.id'))
    operation = Column(String(255), nullable=False)
    status = Column(Enum('success', 'failed', name='operation_status'), nullable=False)
    details = Column(String(1024))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='operation_logs')
    ssh_connection = relationship('SshConnectionLog', back_populates='operation_logs')


class ServerCategoryAssociation(db.Model):
    __tablename__ = 'server_category_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    category_id = Column(Integer, ForeignKey('server_categories.id'))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    server = relationship("Server")
    category = relationship("ServerCategory")


class ServerUpdateLog(db.Model):
    __tablename__ = 'server_update_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    operation_type = Column(Enum('add', 'update', 'delete', name='update_operation'))
    operation_details = Column(String(1024))
    performed_by = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")
    user = relationship("User", foreign_keys=[performed_by])


class UserHistory(db.Model):
    __tablename__ = 'user_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    action = Column(String(255), nullable=False)
    details = Column(String(1024))
    ip_address = Column(String(255))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

    __table_args__ = (
        Index('idx_user_history_user', 'user_id'),
        Index('idx_user_history_created', 'created_at'),
    )


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Enum('debug', 'info', 'warning', 'error', 'critical', name='log_level'), nullable=False)
    module = Column(String(255))  # 记录日志来源的模块
    message = Column(String(1024))
    details = Column(String(1024))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    operation = Column(String(255), nullable=False)  # 新增 operation 字段
    ip_address = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

    __table_args__ = (
        Index('idx_system_log_level', 'level'),
        Index('idx_system_log_module', 'module'),
        Index('idx_system_log_created', 'created_at'),
    )


class UserContainer(db.Model):
    __tablename__ = 'user_containers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    container_id = Column(Integer, ForeignKey('docker_containers.id', ondelete='CASCADE'))
    status = Column(Enum('active', 'inactive', 'suspended', name='user_container_status'), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expiry_date = Column(DateTime)
    
    user = relationship("User")
    container = relationship("DockerContainer")

    __table_args__ = (
        Index('idx_user_container_user', 'user_id'),
        Index('idx_user_container_status', 'status'),
        Index('idx_user_container_expiry', 'expiry_date'),
    )


class MonitoringLog(db.Model):
    __tablename__ = 'monitoring_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id', ondelete='CASCADE'))
    log_type = Column(Enum('performance', 'health', 'traffic', name='monitoring_type'), nullable=False)
    metrics = Column(JSON, default=dict)  # 存储监控指标
    status = Column(Enum('normal', 'warning', 'critical', name='monitoring_status'), default='normal')
    created_at = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")

    __table_args__ = (
        Index('idx_monitoring_server', 'server_id'),
        Index('idx_monitoring_type', 'log_type'),
        Index('idx_monitoring_status', 'status'),
        Index('idx_monitoring_created', 'created_at'),
    )


class SystemAlert(db.Model):
    __tablename__ = 'system_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(Enum('server', 'container', 'traffic', 'security', name='alert_type'), nullable=False)
    severity = Column(Enum('low', 'medium', 'high', 'critical', name='alert_severity'), nullable=False)
    target_id = Column(Integer)  # 可以是服务器ID、容器ID等
    target_type = Column(String(50))  # 标识target_id的类型
    message = Column(String(1024), nullable=False)
    details = Column(JSON, default=dict)
    status = Column(Enum('active', 'acknowledged', 'resolved', name='alert_status'), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index('idx_alert_type', 'alert_type'),
        Index('idx_alert_severity', 'severity'),
        Index('idx_alert_status', 'status'),
        Index('idx_alert_created', 'created_at'),
    )


class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notification_type = Column(Enum('email', 'sms', 'push', 'system', name='notification_type'), nullable=False)
    title = Column(String(255))
    content = Column(String(1024))
    status = Column(Enum('pending', 'sent', 'failed', name='notification_status'), default='pending')
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(String(1024))
    
    user = relationship("User")

    __table_args__ = (
        Index('idx_notification_user', 'user_id'),
        Index('idx_notification_type', 'notification_type'),
        Index('idx_notification_status', 'status'),
        Index('idx_notification_created', 'created_at'),
    )
