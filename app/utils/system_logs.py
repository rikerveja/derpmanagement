from flask import Blueprint, request, jsonify
from app.models import SystemLog
from app import db
import logging

# 定义蓝图
logs_bp = Blueprint('logs', __name__)

# 更新操作日志
@logs_bp.route('/api/logs/update/<int:id>', methods=['PUT'])
def update_log(id):
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
        logging.error(f"Error updating log: {e}")
        return jsonify({"success": False, "message": f"Error updating log: {str(e)}"}), 500

# 删除操作日志
@logs_bp.route('/api/logs/delete/<int:id>', methods=['DELETE'])
def delete_log(id):
    log = SystemLog.query.get(id)
    if not log:
        return jsonify({"success": False, "message": "Log not found"}), 404

    try:
        db.session.delete(log)
        db.session.commit()
        return jsonify({"success": True, "message": "Log deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting log: {e}")
        return jsonify({"success": False, "message": f"Error deleting log: {str(e)}"}), 500
