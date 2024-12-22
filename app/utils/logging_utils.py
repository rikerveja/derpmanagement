from app.models import SystemLog, db
from flask import request
from datetime import datetime
import logging

# 配置全局日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app_logs")

def log_operation_to_db(user_id, operation, status, details=None):
    """
    写入系统操作日志到数据库
    :param user_id: 操作者的用户 ID（可为空）
    :param operation: 操作名称
    :param status: 操作状态（success, failed）
    :param details: 操作详细信息
    """
    ip_address = request.remote_addr if request else "Unknown"
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
        logger.info(f"[DB LOG] Operation logged: User {user_id}, Operation {operation}, Status {status}")
    except Exception as e:
        logger.error(f"Failed to log operation to DB: {e}")
        db.session.rollback()
        # 捕获日志写入失败的错误，避免系统崩溃


def log_operation_to_file(operation, message, level="INFO"):
    """
    写入系统操作日志到文件
    :param operation: 操作名称
    :param message: 日志消息
    :param level: 日志级别（INFO, WARNING, ERROR）
    """
    if level == "INFO":
        logger.info(f"[{operation}] {message}")
    elif level == "WARNING":
        logger.warning(f"[{operation}] {message}")
    elif level == "ERROR":
        logger.error(f"[{operation}] {message}")
    else:
        logger.info(f"[{operation}] {message}")


def log_operation(user_id, operation, status, details=None, to_file=False):
    """
    写入系统操作日志（可选写入文件或数据库）
    :param user_id: 操作者的用户 ID（可为空）
    :param operation: 操作名称
    :param status: 操作状态（success, failed）
    :param details: 操作详细信息
    :param to_file: 是否写入日志文件
    """
    try:
        if to_file:
            log_operation_to_file(operation, f"User {user_id}, Status {status}, Details: {details}", level="INFO")
        else:
            log_operation_to_db(user_id, operation, status, details)
    except Exception as e:
        # 捕获日志记录的异常，避免日志记录错误导致系统崩溃
        logger.error(f"Error in log_operation: {str(e)}")
