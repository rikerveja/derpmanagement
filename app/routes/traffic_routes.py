from flask import Blueprint, jsonify
from app.models import UserContainer
import random

traffic_bp = Blueprint('traffic', __name__)

@traffic_bp.route('/stats/<int:container_id>', methods=['GET'])
def container_traffic_stats(container_id):
    """
    获取容器的实时流量统计
    """
    container = UserContainer.query.get(container_id)
    if not container:
        return jsonify({"success": False, "message": "Container not found"}), 404

    # 示例流量数据（应从实际监控系统获取）
    stats = {
        "container_id": container.id,
        "user_id": container.user_id,
        "server_id": container.server_id,
        "total_traffic": random.randint(1000, 5000),  # 假设的总流量
        "current_speed": random.randint(10, 100)  # 假设的当前速率
    }
    return jsonify({"success": True, "traffic_stats": stats}), 200
