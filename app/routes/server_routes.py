from flask import Blueprint, request, jsonify
from app.models import Server, ServerCategory
from app.utils.server_utils import get_server_status, monitor_server_health
from app import db
import logging

# 定义蓝图
server_bp = Blueprint('server', __name__)

# 添加服务器
@server_bp.route('/api/add_server', methods=['POST'])
def add_server():
    """
    添加新服务器
    """
    data = request.json

    # 获取输入数据
    ip_address = data.get('ip')  # 修正：从请求中获取 ip 并存储为 ip_address
    region = data.get('region')
    storage = data.get('storage', 0.0)  # 这里用 storage 替代 load 字段
    cpu = data.get('cpu')  # 新增：CPU 配置
    memory = data.get('memory')  # 新增：内存配置
    category_id = data.get('category_id')  # 新增：服务器分类ID
    server_name = data.get('server_name')  # 新增：服务器名称
    bandwidth = data.get('bandwidth', 100)  # 新增：带宽，默认100M
    server_type = data.get('server_type')  # 新增：服务器类型
    user_count = data.get('user_count', 0)  # 新增：用户数，默认为0
    total_traffic = data.get('total_traffic', 20)  # 新增：总流量，默认为20GB
    remaining_traffic = total_traffic  # 初始剩余流量等于总流量

    # 检查必填字段
    if not ip_address or not region or not cpu or not memory or not storage or not category_id or not server_name:
        logging.error("Missing required fields: ip_address, region, cpu, memory, storage, category_id, server_name")
        return jsonify({"success": False, "message": "Missing required fields (ip_address, region, cpu, memory, storage, category_id, server_name)"}), 400

    # 检查服务器是否已存在
    existing_server = Server.query.filter_by(ip_address=ip_address).first()  # 使用 ip_address 查询
    if existing_server:
        logging.error(f"Server with IP address {ip_address} already exists")
        return jsonify({"success": False, "message": "Server already exists"}), 400

    # 检查分类是否存在
    category = ServerCategory.query.get(category_id)
    if not category:
        logging.error(f"Category with ID {category_id} not found")
        return jsonify({"success": False, "message": f"Category with ID {category_id} not found"}), 404

    # 创建新服务器对象
    server = Server(
        ip_address=ip_address,
        region=region,
        storage=storage,
        cpu=cpu,
        memory=memory,
        category_id=category_id,
        server_name=server_name,
        bandwidth=bandwidth,
        server_type=server_type,
        user_count=user_count,
        total_traffic=total_traffic,
        remaining_traffic=remaining_traffic
    )

    # 保存新服务器到数据库
    db.session.add(server)
    try:
        db.session.commit()
        logging.info(f"Server added successfully: {ip_address}")
        return jsonify({
            "success": True, 
            "message": "Server added successfully", 
            "server_id": server.id, 
            "ip_address": ip_address,  # 返回 ip_address
            "storage": storage,  # 返回 storage
            "cpu": cpu, 
            "memory": memory,
            "server_name": server_name,
            "bandwidth": bandwidth,
            "server_type": server_type,
            "user_count": user_count,
            "total_traffic": total_traffic,
            "remaining_traffic": remaining_traffic
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding server: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 获取所有服务器
@server_bp.route('/api/get_servers', methods=['GET'])
def get_servers():
    """
    获取所有服务器的列表
    """
    try:
        servers = Server.query.all()
        if not servers:
            logging.info("No servers found")
            return jsonify({"success": False, "message": "No servers found"}), 404

        server_list = []
        for server in servers:
            server_info = {
                'id': server.id,
                'server_name': server.server_name,  # 使用 server_name
                'ip_address': server.ip_address,  # 使用 ip_address
                'region': server.region,
                'storage': server.storage,  # 使用 storage
                'cpu': server.cpu,
                'memory': server.memory,
                'category': server.category.category_name if server.category else None,
                'bandwidth': server.bandwidth,  # 使用 bandwidth
                'server_type': server.server_type,  # 使用 server_type
                'user_count': server.user_count,  # 使用 user_count
                'total_traffic': server.total_traffic,  # 使用 total_traffic
                'remaining_traffic': server.remaining_traffic,  # 使用 remaining_traffic
                'status': server.status,
                'created_at': server.created_at,
                'updated_at': server.updated_at
            }
            server_list.append(server_info)

        return jsonify({"success": True, "servers": server_list}), 200
    except Exception as e:
        logging.error(f"Error retrieving servers: {e}")
        return jsonify({"success": False, "message": f"Error retrieving servers: {str(e)}"}), 500


# 更新服务器状态
@server_bp.route('/api/update_server/<int:server_id>', methods=['PUT'])
def update_server(server_id):
    """
    更新指定服务器的状态
    """
    data = request.json
    new_status = data.get('status')

    if not new_status:
        logging.error("Missing 'status' field")
        return jsonify({"success": False, "message": "Missing 'status' field"}), 400

    server = Server.query.get(server_id)
    if not server:
        logging.error(f"Server with ID {server_id} not found")
        return jsonify({"success": False, "message": "Server not found"}), 404

    try:
        server.status = new_status
        db.session.commit()
        logging.info(f"Updated server {server_id} status to {new_status}")
        return jsonify({"success": True, "message": "Server status updated successfully", "server_id": server_id, "status": new_status}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating server {server_id} status: {e}")
        return jsonify({"success": False, "message": f"Error updating server status: {str(e)}"}), 500


# 删除服务器
@server_bp.route('/api/delete_server/<int:server_id>', methods=['DELETE'])
def delete_server(server_id):
    """
    删除指定服务器
    """
    server = Server.query.get(server_id)
    if not server:
        logging.error(f"Server with ID {server_id} not found")
        return jsonify({"success": False, "message": "Server not found"}), 404

    try:
        db.session.delete(server)
        db.session.commit()
        logging.info(f"Server {server_id} deleted successfully")
        return jsonify({"success": True, "message": f"Server {server_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting server {server_id}: {e}")
        return jsonify({"success": False, "message": f"Error deleting server: {str(e)}"}), 500


# 获取服务器状态
@server_bp.route('/api/server/status/<int:server_id>', methods=['GET'])
def server_status(server_id):
    """
    获取指定服务器的状态
    """
    server = Server.query.get(server_id)
    if not server:
        logging.error(f"Server with ID {server_id} not found")
        return jsonify({"success": False, "message": "Server not found"}), 404

    try:
        # 获取服务器状态
        status = get_server_status(server.ip_address)  # 使用 ip_address
        logging.info(f"Fetched status for server {server_id}: {status}")
        return jsonify({"success": True, "status": status, "storage": server.storage}), 200  # 使用 storage
    except Exception as e:
        logging.error(f"Error getting server status for server {server_id}: {e}")
        return jsonify({"success": False, "message": f"Error getting server status: {str(e)}"}), 500


# 监控服务器健康
@server_bp.route('/api/server/health_check', methods=['GET'])
def health_check():
    """
    监控所有服务器的健康状况
    """
    try:
        # 监控所有服务器的健康状况
        results = monitor_server_health()
        logging.info("Health check completed successfully")
        return jsonify({"success": True, "health_check_results": results}), 200
    except Exception as e:
        logging.error(f"Error during health check: {e}")
        return jsonify({"success": False, "message": f"Error during health check: {str(e)}"}), 500
