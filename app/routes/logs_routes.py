from flask import Blueprint, request, jsonify
from app.models import UserLog, ServerLog
from app import db
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

logs_bp = Blueprint('logs', __name__)

# 配置日志记录
logger = logging.getLogger('app_logs')
handler = RotatingFileHandler("system.log", maxBytes=1000000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@logs_bp.route('/api/logs/system', methods=['GET'])
def get_system_logs():
    """
    查询系统日志
    """
    logs = UserLog.query.order_by(UserLog.timestamp.desc()).limit(100).all()
    log_data = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "timestamp": log.timestamp,
        } for log in logs
    ]
    return jsonify({"success": True, "logs": log_data}), 200
