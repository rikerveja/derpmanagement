from app.models import SystemLog, db
from flask import request
from datetime import datetime

def log_operation(user_id, operation, status, details=None):
    """
    写入系统操作日志
    :param user_id: 操作者的用户 ID（可为空）
    :param operation: 操作名称
    :param status: 操作状态（success, failed）
    :param details: 操作详细信息
    """
    ip_address = request.remote_addr
    log = SystemLog(
        user_id=user_id,
        operation=operation,
        status=status,
        ip_address=ip_address,
        details=details,
        timestamp=datetime.utcnow()
    )
    try:
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log operation: {e}")
        db.session.rollback()
