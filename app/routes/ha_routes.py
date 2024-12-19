from flask import Blueprint, jsonify
import random

# 定义蓝图
ha_bp = Blueprint('ha', __name__)

# 模拟服务器状态
server_health = {
    "server_1": "healthy",
    "server_2": "healthy",
    "server_3": "unhealthy"
}

# 查看服务器运行状态
@ha_bp.route('/api/ha/health', methods=['GET'])
def check_server_health():
    """
    查看服务器健康状态
    """
    return jsonify({"success": True, "server_health": server_health}), 200


# 故障切换
@ha_bp.route('/api/ha/failover', methods=['POST'])
def failover():
    """
    故障切换服务到备用服务器
    """
    unhealthy_servers = [key for key, status in server_health.items() if status == "unhealthy"]
    if not unhealthy_servers:
        return jsonify({"success": False, "message": "No unhealthy servers detected"}), 200

    # 模拟切换到备用服务器
    for server in unhealthy_servers:
        server_health[server] = "switched"

    return jsonify({"success": True, "message": "Failover completed", "updated_health": server_health}), 200
