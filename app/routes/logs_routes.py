from flask import Blueprint, request, jsonify
from app.models import UserLog, SystemLog, db
import logging
from logging.handlers import RotatingFileHandler
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


# 查询系统日志
@logs_bp.route('/api/logs/system', methods=['GET'])
def get_system_logs():
    """
    查询系统日志
    """
    try:
        logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(100).all()
        log_data = [
            {
                "id": log.id,
                "user_id": log.user_id,
                "operation": log.operation,
                "status": log.status,
                "timestamp": log.timestamp.isoformat(),  # 转换为 ISO 格式
                "details": log.details
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
        logger.error(f"Invalid date format or error querying logs: {str(e)}")
        return jsonify({"success": False, "message": "Invalid date format. Expected format: YYYY-MM-DD HH:MM:SS"}), 400
    except Exception as e:
        logger.error(f"Error querying logs: {str(e)}")
        return jsonify({"success": False, "message": f"Error querying logs: {str(e)}"}), 500


# 更新系统日志
@logs_bp.route('/api/logs/update/<int:id>', methods=['PUT'])
def update_log(id):
    """
    更新系统日志
    """
    data = request.json
    status = data.get('status')
    details = data.get('details')

    log = SystemLog.query.get(id)
    if not log:
        return jsonify({"success": False, "message": "Log not found"}), 404

    try:
        log.status = status if status else log.status
        log.details = details if details else log.details
        db.session.commit()
        return jsonify({"success": True, "message": "Log updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating log: {e}")
        return jsonify({"success": False, "message": f"Error updating log: {str(e)}"}), 500


# 删除系统日志
@logs_bp.route('/api/logs/delete/<int:id>', methods=['DELETE'])
def delete_log(id):
    """
    删除系统日志
    """
    log = SystemLog.query.get(id)
    if not log:
        return jsonify({"success": False, "message": "Log not found"}), 404

    try:
        db.session.delete(log)
        db.session.commit()
        return jsonify({"success": True, "message": "Log deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting log: {e}")
        return jsonify({"success": False, "message": f"Error deleting log: {str(e)}"}), 500
