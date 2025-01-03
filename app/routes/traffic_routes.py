from flask import Blueprint, request, jsonify
from app.models import UserContainer
from datetime import datetime, timedelta
import random
import logging

# 定义蓝图
traffic_bp = Blueprint('traffic', __name__)

# 模拟存储流量数据
traffic_data = {}

# 实时流量监控（所有容器）
@traffic_bp.route('/api/traffic/realtime', methods=['GET'])
def realtime_traffic():
    """
    获取所有容器的实时流量监控
    """
    try:
        traffic_data = [
            {
                "container_id": container.id,
                "server_id": container.server_id,
                "port": container.port,
                "stun_port": container.stun_port,
                "realtime_rate": round(random.uniform(1.0, 100.0), 2),  # Mbps
                "timestamp": datetime.utcnow().isoformat()  # 流量更新时间戳
            }
            for container in UserContainer.query.all()
        ]
        return jsonify({"success": True, "traffic_data": traffic_data}), 200
    except Exception as e:
        logging.error(f"Error fetching realtime traffic data: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching realtime traffic: {str(e)}"}), 500


# 实时流量监控（单个容器）
@traffic_bp.route('/api/traffic/realtime/<int:container_id>', methods=['GET'])
def get_realtime_traffic(container_id):
    """
    获取容器的实时流量数据
    """
    try:
        # 获取容器实时流量数据，模拟数据
        traffic = traffic_data.get(container_id, {"upload": random.randint(0, 500), "download": random.randint(0, 500)})
        timestamp = datetime.utcnow().isoformat()
        return jsonify({"success": True, "traffic": traffic, "timestamp": timestamp}), 200
    except Exception as e:
        logging.error(f"Error fetching realtime traffic for container {container_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching realtime traffic: {str(e)}"}), 500


# 用户流量历史统计
@traffic_bp.route('/api/traffic/history/<int:user_id>', methods=['GET'])
def traffic_history(user_id):
    """
    获取用户的流量历史统计
    """
    try:
        # 模拟历史流量数据（最近7天）
        history_data = [
            {
                "date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "traffic_used": round(random.uniform(0.5, 10.0), 2),  # GB
                "peak_traffic": round(random.uniform(1.0, 5.0), 2),  # 高峰流量（GB）
            }
            for i in range(7)
        ]
        return jsonify({"success": True, "user_id": user_id, "history_data": history_data}), 200
    except Exception as e:
        logging.error(f"Error fetching traffic history for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching traffic history: {str(e)}"}), 500


# 按用户或服务器统计流量
@traffic_bp.route('/api/traffic/stats', methods=['POST'])
def get_traffic_stats():
    """
    按用户或服务器统计流量
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    try:
        if user_id:
            # 按用户统计流量
            user_containers = UserContainer.query.filter_by(user_id=user_id).all()
            user_traffic = {
                container.id: {
                    "upload": random.randint(0, 500),
                    "download": random.randint(0, 500)
                }
                for container in user_containers
            }
            return jsonify({"success": True, "user_traffic": user_traffic}), 200

        if server_id:
            # 按服务器统计流量
            server_containers = UserContainer.query.filter_by(server_id=server_id).all()
            server_traffic = {
                container.id: {
                    "upload": random.randint(0, 500),
                    "download": random.randint(0, 500)
                }
                for container in server_containers
            }
            return jsonify({"success": True, "server_traffic": server_traffic}), 200

        return jsonify({"success": False, "message": "Missing user_id or server_id"}), 400
    except Exception as e:
        logging.error(f"Error fetching traffic stats: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching traffic stats: {str(e)}"}), 500


# 超流量检测
@traffic_bp.route('/api/traffic/overlimit', methods=['GET'])
def detect_overlimit_users():
    """
    检测超流量用户
    """
    try:
        overlimit_users = []
        for container_id, traffic in traffic_data.items():
            total_traffic = traffic.get('upload', 0) + traffic.get('download', 0)
            if total_traffic > 1000:  # 假设超流量阈值为 1000MB
                overlimit_users.append({"container_id": container_id, "total_traffic": total_traffic})

        return jsonify({"success": True, "overlimit_users": overlimit_users}), 200
    except Exception as e:
        logging.error(f"Error detecting overlimit users: {str(e)}")
        return jsonify({"success": False, "message": f"Error detecting overlimit users: {str(e)}"}), 500
