from flask import Blueprint, request, jsonify
import logging
from logging.handlers import RotatingFileHandler

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


# 记录操作日志
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


# 查询日志
@logs_bp.route('/api/logs/query', methods=['GET'])
def query_logs():
    """
    查询操作日志
    """
    try:
        with open("system.log", "r") as log_file:
            logs = log_file.readlines()
        return jsonify({"success": True, "logs": logs}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error reading logs: {str(e)}"}), 500
