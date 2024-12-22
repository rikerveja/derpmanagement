from flask import Blueprint, request, jsonify
from app.utils.docker_utils import create_container, stop_container, get_container_status, list_containers, update_container
import logging

# 定义蓝图
container_bp = Blueprint('container', __name__)

# 获取容器列表
@container_bp.route('/api/containers', methods=['GET'])
def get_containers():
    """
    获取容器列表，支持过滤所有容器和仅获取当前用户容器。
    """
    all_containers = request.args.get('all', 'false').lower() == 'true'
    try:
        containers = list_containers(all=all_containers)
        container_list = [{'id': c.id, 'name': c.name, 'status': c.status} for c in containers]
        return jsonify({"success": True, "containers": container_list}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching containers: {str(e)}"}), 500

# 创建新容器
@container_bp.route('/api/containers', methods=['POST'])
def create_new_container():
    """
    创建一个新的 Docker 容器
    """
    data = request.json
    image_name = data.get('image_name')
    container_name = data.get('container_name')
    ports = data.get('ports')
    environment = data.get('environment', None)

    # 检查必填字段
    if not image_name or not container_name or not ports:
        return jsonify({"success": False, "message": "Missing required parameters"}), 400

    try:
        container = create_container(image_name, container_name, ports, environment)
        if container:
            return jsonify({"success": True, "message": f"Container {container_name} created successfully"}), 201
        else:
            return jsonify({"success": False, "message": "Failed to create container"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error creating container: {str(e)}"}), 500

# 停止容器
@container_bp.route('/api/containers/<container_name>/stop', methods=['POST'])
def stop_existing_container(container_name):
    """
    停止一个正在运行的容器
    """
    try:
        result = stop_container(container_name)
        if result:
            return jsonify({"success": True, "message": f"Container {container_name} stopped successfully"}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to stop container {container_name}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error stopping container {container_name}: {str(e)}"}), 500

# 获取容器状态
@container_bp.route('/api/containers/<container_name>/status', methods=['GET'])
def get_container_status_route(container_name):
    """
    获取容器的当前状态
    """
    try:
        status = get_container_status(container_name)
        if status:
            return jsonify({"success": True, "container_name": container_name, "status": status}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to retrieve status for container {container_name}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error retrieving status for container {container_name}: {str(e)}"}), 500


# 更新容器
@container_bp.route('/api/containers/<container_name>', methods=['PUT'])
def update_existing_container(container_name):
    """
    更新容器配置（如 ports, environment 等）
    """
    data = request.json
    ports = data.get('ports')
    environment = data.get('environment', None)

    # 检查必填字段
    if not ports:
        return jsonify({"success": False, "message": "Missing required parameters (ports)"}), 400

    try:
        # 调用更新容器的函数
        result = update_container(container_name, ports, environment)
        if result:
            return jsonify({"success": True, "message": f"Container {container_name} updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to update container {container_name}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating container: {str(e)}"}), 500
