from flask import Blueprint, jsonify
import os

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/view', methods=['GET'])
def view_logs():
    """
    查看操作日志
    """
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.readlines()
        return jsonify({"success": True, "logs": logs}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Log file not found"}), 404
