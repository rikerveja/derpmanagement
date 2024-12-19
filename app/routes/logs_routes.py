from flask import Blueprint, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
from app.models import UserLog, ServerLog, db
from datetime import datetime

# 定义蓝图
logs_bp = Blueprint('logs', __name__)

# 配置日志记录
logger = logging.getLogger('app_logs')
handler = RotatingFileHandler("system.log", maxBytes=1000000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 记录系统日志
@logs_bp.route('/api/logs/record', methods=['POST'])
def record_log():
    """
    记录系统操作日志
    """
    data = request.json
    message = data.get('message')
    level = data.get('level', 'INFO')

    if not message:
        return jsonify({"success": False, "message": "Missing log message"}), 400

    if level.upper() == 'INFO':
        logger.info(message)
    elif level.upper() == 'ERROR':
        logger.error(message)
    elif level.upper() == 'WARNING':
        logger.warning(message)
    else:
        return jsonify({"success": False, "message": "Invalid log level"}), 400

    return jsonify({"success": True, "message": "Log recorded successfully"}), 200


# 查询系统日志
@logs_bp.route('/api/logs/query', methods=['GET'])
def query_logs():
    """
    查询系统日志
    支持按日志级别、关键字、时间范围查询
    """
    level = request.args.get('level')
    keyword = request.args.get('keyword')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    try:
        with open("system.log", "r") as log_file:
            logs = log_file.readlines()

        # 筛选日志
        if level:
            logs = [log for log in logs if f"{level.upper()}" in log]
        if keyword:
            logs = [log for log in logs if keyword in log]
        if start_time:
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            logs = [log for log in logs if datetime.strptime(log.split("]")[0][1:], "%Y-%m-%d %H:%M:%S") >= start_time]
        if end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            logs = [log for log in logs if datetime.strptime(log.split("]")[0][1:], "%Y-%m-%d %H:%M:%S") <= end_time]

        return jsonify({"success": True, "logs": logs}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error reading logs: {str(e)}"}), 500


# 记录用户操作日志
@logs_bp.route('/api/logs/user', methods=['POST'])
def record_user_log():
    """
    记录用户操作日志
    """
    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')

    if not user_id or not action:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user_log = UserLog(user_id=user_id, action=action)
    db.session.add(user_log)
    try:
        db.session.commit()
        logger.info(f"User {user_id} performed action: {action}")
        return jsonify({"success": True, "message": "User log recorded successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to record user log: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 记录服务器事件日志
@logs_bp.route('/api/logs/server', methods=['POST'])
def record_server_log():
    """
    记录服务器事件日志
    """
    data = request.json
    server_id = data.get('server_id')
    event = data.get('event')

    if not server_id or not event:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    server_log = ServerLog(server_id=server_id, event=event)
    db.session.add(server_log)
    try:
        db.session.commit()
        logger.info(f"Server {server_id} event recorded: {event}")
        return jsonify({"success": True, "message": "Server log recorded successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to record server log: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 查询用户操作日志
@logs_bp.route('/api/logs/user/<int:user_id>', methods=['GET'])
def get_user_logs(user_id):
    """
    查询用户操作日志
    """
    logs = UserLog.query.filter_by(user_id=user_id).all()
    log_data = [{"id": log.id, "action": log.action, "timestamp": log.timestamp} for log in logs]
    return jsonify({"success": True, "logs": log_data}), 200


# 查询服务器事件日志
@logs_bp.route('/api/logs/server/<int:server_id>', methods=['GET'])
def get_server_logs(server_id):
    """
    查询服务器事件日志
    """
    logs = ServerLog.query.filter_by(server_id=server_id).all()
    log_data = [{"id": log.id, "event": log.event, "timestamp": log.timestamp} for log in logs]
    return jsonify({"success": True, "logs": log_data}), 200
