from flask import Blueprint, jsonify

# 定义蓝图
monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/api/monitoring', methods=['GET'])
def get_monitoring_status():
    """
    返回一个简单的监控状态
    """
    return jsonify({"success": True, "message": "Monitoring is active!"}), 200
