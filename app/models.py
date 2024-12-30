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

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, DECIMAL, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
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
    notifications = relationship("RenewalNotification", back_populates="user")


class UserLog(Base):
    __tablename__ = 'user_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    operation = Column(String(255))
    details = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(255))
    user_agent = Column(String(255))

    user = relationship("User", back_populates="logs")


class RolePermission(Base):
    __tablename__ = 'roles_permissions'

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), unique=True, nullable=False)
    permissions = Column(String)


class DistributorCommission(Base):
    __tablename__ = 'distributor_commission'

    id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_id = Column(Integer, ForeignKey('users.id'))
    serial_number = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('pending', 'paid', name='commission_status'), default='pending')

    distributor = relationship("User", back_populates="commissions")


class Rental(Base):
    __tablename__ = 'rentals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('active', 'expired', 'paused', name='rental_status'), default='active', nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    server_ids = Column(JSON)
    container_ids = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(Integer)

    user = relationship("User", back_populates="rentals")


class RenewalNotification(Base):
    __tablename__ = 'renewal_notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    notification_type = Column(Enum('7_days', '3_days', '1_day', name='notification_type'))
    sent_at = Column(DateTime, default=datetime.utcnow)
    notification_channel = Column(Enum('email', 'sms', 'push', name='notification_channel'))
    notification_sent = Column(Boolean, default=False)
    notification_status = Column(Enum('pending', 'sent', 'failed', name='notification_status'), default='pending')
    notification_content = Column(String)

    user = relationship("User", back_populates="notifications")


class Distributor(Base):
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

    __table_args__ = (
        UniqueConstraint('email', name='unique_distributor_email'),
    )


class SerialNumber(Base):
    __tablename__ = 'serial_numbers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), unique=True, nullable=False)
    status = Column(Enum('unused', 'used', 'expired', name='serial_number_status'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    valid_days = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    activated_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    used_at = Column(DateTime)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))
    payment_status = Column(Enum('paid', 'unpaid', name='payment_status'), default='unpaid')

    user = relationship("User", back_populates="serial_numbers")
    distributor = relationship("Distributor", back_populates="serial_numbers")


class SerialUserAssociation(Base):
    __tablename__ = 'serial_user_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    status = Column(Enum('activated', 'pending', 'expired', name='serial_status'), default='pending')
    activated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    serial_number = relationship("SerialNumber")


class ServerCategory(Base):
    __tablename__ = 'server_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255), nullable=False)


class Server(Base):
    __tablename__ = 'servers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_name = Column(String(255), nullable=False)
    ip_address = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey('server_categories.id'))
    cpu = Column(String(50))
    memory = Column(String(50))
    storage = Column(String(50))
    bandwidth = Column(String(255))
    status = Column(Enum('healthy', 'unhealthy', 'maintenance', name='server_status'), default='healthy')
    server_type = Column(String(255))
    region = Column(String(255))
    user_count = Column(Integer, default=0)
    total_traffic = Column(Integer)
    remaining_traffic = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("ServerCategory")


class DockerContainer(Base):
    __tablename__ = 'docker_containers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String(255), unique=True, nullable=False)
    server_id = Column(Integer, ForeignKey('servers.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    port = Column(Integer)
    stun_port = Column(Integer)
    status = Column(Enum('running', 'stopped', 'paused', 'restarting', 'exited', name='container_status'), default='running')
    image = Column(String(255))
    max_upload_traffic = Column(DECIMAL(10, 2))
    max_download_traffic = Column(DECIMAL(10, 2))
    upload_traffic = Column(DECIMAL(10, 2))
    download_traffic = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    server = relationship("Server")
    user = relationship("User")


class SerialServerAssociation(Base):
    __tablename__ = 'serial_server_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    server_id = Column(Integer, ForeignKey('servers.id'))
    container_id = Column(Integer, ForeignKey('docker_containers.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    serial_number = relationship("SerialNumber")
    server = relationship("Server")
    container = relationship("DockerContainer")


class SerialHistory(Base):
    __tablename__ = 'serial_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    operation = Column(Enum('generated', 'activated', 'expired', name='serial_history_status'), nullable=False)
    details = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    serial_number = relationship("SerialNumber")


class ServerContainerAssociation(Base):
    __tablename__ = 'server_container_association'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    server = relationship("Server")
    container = relationship("DockerContainer")


class ServerHistory(Base):
    __tablename__ = 'server_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    operation = Column(Enum('status_change', 'maintenance', 'downtime', 'restore', name='server_operation'))
    details = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")


class ServerTrafficMonitoring(Base):
    __tablename__ = 'server_traffic_monitoring'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    total_traffic = Column(Integer)
    used_traffic = Column(Integer)
    remaining_traffic = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")


class ServerPerformanceMonitoring(Base):
    __tablename__ = 'server_performance_monitoring'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    cpu_usage = Column(DECIMAL(10, 2))
    memory_usage = Column(DECIMAL(10, 2))
    network_latency = Column(DECIMAL(10, 2))
    timestamp = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server")


class DockerContainerResources(Base):
    __tablename__ = 'docker_container_resources'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    cpu_limit = Column(DECIMAL(10, 2))
    memory_limit = Column(DECIMAL(10, 2))
    disk_limit = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    container = relationship("DockerContainer")


class DockerContainerTraffic(Base):
    __tablename__ = 'docker_container_traffic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    upload_traffic = Column(DECIMAL(10, 2))
    download_traffic = Column(DECIMAL(10, 2))
    timestamp = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")


class DockerContainerEvents(Base):
    __tablename__ = 'docker_container_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    event_type = Column(Enum('start', 'stop', 'restart', 'pause', 'unpause', 'error', name='container_event_type'))
    event_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")


class DockerContainerLogs(Base):
    __tablename__ = 'docker_container_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(Integer, ForeignKey('docker_containers.id'))
    log_level = Column(Enum('info', 'warn', 'error', name='log_level'))
    log_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    container = relationship("DockerContainer")


class ACLConfig(Base):
    __tablename__ = 'acl_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    server_ids = Column(JSON)
    container_ids = Column(JSON)
    acl_data = Column(JSON)
    version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User")


class ACLVerificationLog(Base):
    __tablename__ = 'acl_verification_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    acl_id = Column(Integer, ForeignKey('acl_configs.id'))
    ip_address = Column(String(50))
    location = Column(String(255))
    status = Column(Enum('approved', 'denied', name='verification_status'))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    acl_config = relationship("ACLConfig")


class ACLLog(Base):
    __tablename__ = 'acl_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    operation = Column(Enum('generate', 'update', 'delete', name='acl_operation'))
    acl_config_id = Column(Integer, ForeignKey('acl_configs.id'))
    details = Column(String)
    ip_address = Column(String(255))
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    acl_config = relationship("ACLConfig")


class ACLFilePath(Base):
    __tablename__ = 'acl_file_paths'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    acl_config_id = Column(Integer, ForeignKey('acl_configs.id'))
    file_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    acl_config = relationship("ACLConfig")


class ACLDownloadLog(Base):
    __tablename__ = 'acl_download_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    acl_file_id = Column(Integer, ForeignKey('acl_file_paths.id'))
    download_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(255))

    user = relationship("User")
    acl_file = relationship("ACLFilePath")


class AlarmRule(Base):
    __tablename__ = 'alarm_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(Enum('Brute Force Login Attempt', 'Monthly Traffic Limit Exceeded', 'Server Health Issue', 'Server Resource Mismatch', 'Docker Traffic Issue', 'Docker Container Issue', name='alert_type'))
    alert_condition = Column(String)
    threshold = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlarmLog(Base):
    __tablename__ = 'alarm_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey('alarm_rules.id'))
    server_id = Column(Integer, ForeignKey('servers.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    alert_type = Column(String(255))
    message = Column(String)
    status = Column(Enum('active', 'resolved', 'acknowledged', name='alarm_status'))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.id'))

    rule = relationship("AlarmRule")
    server = relationship("Server")
    user = relationship("User", foreign_keys=[user_id])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])


class AlarmNotification(Base):
    __tablename__ = 'alarm_notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_log_id = Column(Integer, ForeignKey('alarm_logs.id'))
    notification_type = Column(Enum('email', 'sms', 'push', name='notification_channel'))
    status = Column(Enum('sent', 'failed', 'pending', name='notification_status'), default='pending')
    sent_at = Column(DateTime)
    sent_to = Column(String(255))
    notification_content = Column(String)

    alarm_log = relationship("AlarmLog")


class AlarmResolution(Base):
    __tablename__ = 'alarm_resolutions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_log_id = Column(Integer, ForeignKey('alarm_logs.id'))
    action_taken = Column(String)
    resolved_by = Column(Integer, ForeignKey('users.id'))
    resolved_at = Column(DateTime)
    status = Column(Enum('resolved', 'ignored', 'escalated', name='resolution_status'))

    alarm_log = relationship("AlarmLog")
    resolved_by_user = relationship("User")


class Invoice(Base):
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


class PaymentRecord(Base):
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


class DistributorCommission(Base):
    __tablename__ = 'distributor_commissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_id = Column(Integer, ForeignKey('users.id'))
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    commission_amount = Column(DECIMAL(10, 2))
    status = Column(Enum('pending', 'paid', name='commission_status'), default='pending')
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    distributor = relationship("User")
    invoice = relationship("Invoice")


class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String(50), nullable=False)
    account_info = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
