from flask import Blueprint, request, jsonify
from app.models import Server
from app.utils.server_utils import get_server_status, monitor_server_health
from app.utils.notifications_utils import send_general_notification
from app import db
import logging

# 定义蓝图
server_bp = Blueprint('server', __name__)

# 添加服务器
@server_bp.route('/api/add_server', methods=['POST'])
def add_server():
    data = request.json
    ip = data.get('ip')
    region = data.get('region')
    load = data.get('load', 0.0)
    cpu = data.get('cpu')  # 新增：CPU 配置
    memory = data.get('memory')  # 新增：内存配置

    # 检查字段是否完整
    if not ip or not region or not cpu or not memory:
        return jsonify({"success": False, "message": "Missing required fields (ip, region, cpu, memory)"}), 400

    # 检查服务器是否已存在
    existing_server = Server.query.filter_by(ip=ip).first()
    if existing_server:
        return jsonify({"success": False, "message": "Server already exists"}), 400

    # 创建新服务器
    server = Server(ip=ip, region=region, load=load, cpu=cpu, memory=memory)
    db.session.add(server)
    try:
        db.session.commit()
        logging.info(f"Server added successfully: {ip}")
        return jsonify({"success": True, "message": "Server added successfully", "server_id": server.id, "ip": ip, "cpu": cpu, "memory": memory}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding server: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 获取服务器状态
@server_bp.route('/api/server/status/<int:server_id>', methods=['GET'])
def server_status(server_id):
    server = Server.query.get(server_id)
    if not server:
        return jsonify({"success": False, "message": "Server not found"}), 404

    # 获取服务器状态
    try:
        status = get_server_status(server.ip)
        return jsonify({"success": True, "status": status, "load": server.load}), 200
    except Exception as e:
        logging.error(f"Error getting server status: {e}")
        return jsonify({"success": False, "message": f"Error getting server status: {str(e)}"}), 500


# 监控服务器健康
@server_bp.route('/api/server/health_check', methods=['GET'])
def health_check():
    try:
        # 监控所有服务器的健康状况
        results = monitor_server_health()
        return jsonify({"success": True, "health_check_results": results}), 200
    except Exception as e:
        logging.error(f"Error during health check: {e}")
        return jsonify({"success": False, "message": f"Error during health check: {str(e)}"}), 500
