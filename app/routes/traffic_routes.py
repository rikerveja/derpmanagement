from flask import Blueprint, request, jsonify
from app.models import UserContainer
import random

# 定义蓝图
traffic_bp = Blueprint('traffic', __name__)

# 模拟流量数据
traffic_data = {}

# 实时流量监控
@traffic_bp.route('/api/traffic/realtime/<int:container_id>', methods=['GET'])
def get_realtime_traffic(container_id):
    """
    获取容器的实时流量数据
    """
    traffic = traffic_data.get(container_id, {"upload": 0, "download": 0})
    return jsonify({"success": True, "traffic": traffic}), 200


# 流量统计
@traffic_bp.route('/api/traffic/stats', methods=['POST'])
def get_traffic_stats():
    """
    按用户或服务器统计流量
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    if user_id:
        # 按用户统计流量
        user_containers = UserContainer.query.filter_by(user_id=user_id).all()
        user_traffic = {container.id: traffic_data.get(container.id, {"upload": 0, "download": 0}) for container in user_containers}
        return jsonify({"success": True, "user_traffic": user_traffic}), 200

    if server_id:
        # 按服务器统计流量
        server_containers = UserContainer.query.filter_by(server_id=server_id).all()
        server_traffic = {container.id: traffic_data.get(container.id, {"upload": 0, "download": 0}) for container in server_containers}
        return jsonify({"success": True, "server_traffic": server_traffic}), 200

    return jsonify({"success": False, "message": "Missing user_id or server_id"}), 400


# 超流量检测
@traffic_bp.route('/api/traffic/overlimit', methods=['GET'])
def detect_overlimit_users():
    """
    检测超流量用户
    """
    overlimit_users = []
    for container_id, traffic in traffic_data.items():
        total_traffic = traffic.get('upload', 0) + traffic.get('download', 0)
        if total_traffic > 1000:  # 假设超流量阈值为 1000MB
            overlimit_users.append({"container_id": container_id, "total_traffic": total_traffic})

    return jsonify({"success": True, "overlimit_users": overlimit_users}), 200
