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

# 查询系统日志
@logs_bp.route('/api/logs/system', methods=['GET'])
def get_system_logs():
    """
    查询系统日志
    """
    try:
        logs = UserLog.query.order_by(UserLog.timestamp.desc()).limit(100).all()
        log_data = [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),  # 转换为 ISO 格式
            } for log in logs
        ]
        return jsonify({"success": True, "logs": log_data}), 200
    except Exception as e:
        logger.error(f"Error fetching system logs: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching system logs: {str(e)}"}), 500


# 按时间范围查询用户日志
@logs_bp.route('/api/logs/user_by_time', methods=['GET'])
def get_user_logs_by_time():
    """
    按时间范围查询用户日志
    """
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if not start_time or not end_time:
        return jsonify({"success": False, "message": "Both start_time and end_time are required"}), 400

    try:
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        logs = UserLog.query.filter(UserLog.timestamp.between(start, end)).all()
        result = [
            {"id": log.id, "user_id": log.user_id, "action": log.action, "timestamp": log.timestamp.isoformat()} 
            for log in logs
        ]
        return jsonify({"success": True, "logs": result}), 200
    except ValueError as e:
        # 捕获时间格式错误
        logger.error(f"Invalid date format or error querying logs: {str(e)}")
        return jsonify({"success": False, "message": "Invalid date format. Expected format: YYYY-MM-DD HH:MM:SS"}), 400
    except Exception as e:
        logger.error(f"Error querying logs: {str(e)}")
        return jsonify({"success": False, "message": f"Error querying logs: {str(e)}"}), 500
