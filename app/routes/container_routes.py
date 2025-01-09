from flask import Blueprint, request, jsonify
from app.utils.docker_utils import create_container, stop_container, get_container_status, list_containers, update_docker_container, update_traffic_for_container, delete_container_by_id
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
        return jsonify({"success": True, "containers": containers}), 200
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
        # 创建容器实例
        # 假设你有 DockerContainer 模型，你需要在数据库中保存新容器
        new_container = DockerContainer(
            container_id=f"container_{container_name}",  # 假设容器 ID 按照一定规则生成
            container_name=container_name,
            image=image_name,
            port=ports.split(":")[0],  # 假设获取前端端口
            stun_port=ports.split(":")[1] if len(ports.split(":")) > 1 else None,
            node_exporter_port=None,  # 根据需求生成或传入
            status='running',  # 默认状态
            max_upload_traffic=0,  # 初始最大上传流量，可以根据需要调整
            max_download_traffic=0,  # 初始最大下载流量，可以根据需要调整
            upload_traffic=0,  # 初始上传流量
            download_traffic=0,  # 初始下载流量
        )

        # 将新容器保存到数据库
        db.session.add(new_container)
        db.session.commit()

        return jsonify({"success": True, "message": f"Container {container_name} created successfully"}), 201
    except Exception as e:
        db.session.rollback()  # 回滚事务
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

# 获取容器详情
@container_bp.route('/api/containers/<container_id>', methods=['GET'])
def get_container_details(container_id):
    """
    获取指定容器的详细信息
    """
    try:
        container = get_container_by_id(container_id)
        if container:
            return jsonify({"success": True, "container": container}), 200
        else:
            return jsonify({"success": False, "message": "Container not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching container: {str(e)}"}), 500

# 更新容器
@container_bp.route('/api/containers/<container_name>', methods=['PUT'])
def update_existing_container(container_name):
    """
    更新容器配置（如 ports, environment 等）
    """
    data = request.json
    new_image = data.get('new_image')  # 新镜像（如果需要更新镜像）
    ports = data.get('ports')
    environment = data.get('environment', None)

    # 检查必填字段
    if not new_image or not ports:
        return jsonify({"success": False, "message": "Missing required parameters (new_image, ports)"}), 400

    try:
        # 调用更新容器的函数
        result = update_docker_container(container_name, new_image, environment, ports)
        if result:
            return jsonify({"success": True, "message": f"Container {container_name} updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to update container {container_name}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating container: {str(e)}"}), 500

# 更新容器流量
@container_bp.route('/api/containers/<container_id>/update_traffic', methods=['PUT'])
def update_traffic(container_id):
    """
    更新容器的流量（上传和下载）
    """
    data = request.json
    upload_traffic = data.get('upload_traffic')
    download_traffic = data.get('download_traffic')

    if upload_traffic is None and download_traffic is None:
        return jsonify({"success": False, "message": "Missing traffic parameters"}), 400

    try:
        result = update_traffic_for_container(container_id, upload_traffic, download_traffic)
        if result:
            return jsonify({"success": True, "message": "Container traffic updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to update traffic"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating traffic: {str(e)}"}), 500

# 删除容器
@container_bp.route('/api/containers/<container_id>', methods=['DELETE'])
def delete_container(container_id):
    """
    删除指定容器
    """
    try:
        result = delete_container_by_id(container_id)
        if result:
            return jsonify({"success": True, "message": "Container deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to delete container"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error deleting container: {str(e)}"}), 500
