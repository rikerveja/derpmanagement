from flask import Blueprint, request, jsonify
from app.utils.docker_utils import create_container, stop_container, get_container_status, list_containers, update_docker_container, update_traffic_for_container, delete_container_by_id
from app import db
from app.models import DockerContainer  # 假设你有一个名为 DockerContainer 的模型类
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
        # 如果 all_containers 为 True，查询所有容器，否则只查询当前用户的容器
        if all_containers:
            containers = DockerContainer.query.all()  # 查询所有容器
        else:
            # 这里假设可以根据当前用户的服务器ID或者其他标识符来过滤
            user_id = request.args.get('user_id')  # 假设需要用户ID作为过滤条件
            if user_id:
                containers = DockerContainer.query.filter_by(user_id=user_id).all()  # 根据用户ID过滤
            else:
                containers = DockerContainer.query.all()  # 默认查询所有容器

        # 将查询结果转为字典形式，返回所有字段
        containers_list = [
            {
                "id": container.id,
                "container_id": container.container_id,
                "server_id": container.server_id,
                "user_id": container.user_id,
                "port": container.port,
                "stun_port": container.stun_port,
                "status": container.status,
                "image": container.image,
                "max_upload_traffic": container.max_upload_traffic,
                "max_download_traffic": container.max_download_traffic,
                "upload_traffic": container.upload_traffic,
                "download_traffic": container.download_traffic,
                "created_at": container.created_at,
                "updated_at": container.updated_at,
                "node_exporter_port": container.node_exporter_port,
                "container_name": container.container_name
            }
            for container in containers
        ]
        
        return jsonify({"success": True, "containers": containers_list}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching containers: {str(e)}"}), 500


@container_bp.route('/api/containers', methods=['POST'])
def create_new_container():
    """
    创建一个新的 Docker 容器
    """
    data = request.json
    container_id = data.get('container_id')  # 从请求中获取 container_id
    container_name = data.get('container_name')
    server_id = data.get('server_id')
    image = data.get('image')
    port = data.get('port')
    stun_port = data.get('stun_port')
    node_exporter_port = data.get('node_exporter_port')
    max_upload_traffic = data.get('max_upload_traffic', 5)  # 默认值为 5 GB
    max_download_traffic = data.get('max_download_traffic', 5)  # 默认值为 5 GB

    # 检查必填字段
    if not container_id or not container_name or not server_id or not image or not port:
        return jsonify({"success": False, "message": "Missing required parameters"}), 400

    try:
        # 创建容器实例并保存到数据库
        new_container = DockerContainer(
            container_id=container_id,  # 根据传递的 container_id 存入数据库
            container_name=container_name,  # 根据传递的 container_name 存入数据库
            server_id=server_id,
            image=image,
            port=port,
            stun_port=stun_port,
            node_exporter_port=node_exporter_port,
            max_upload_traffic=max_upload_traffic,
            max_download_traffic=max_download_traffic,
            status='running',  # 默认状态
            upload_traffic=0,  # 初始上传流量
            download_traffic=0,  # 初始下载流量
        )

        # 将新容器保存到数据库
        db.session.add(new_container)
        db.session.commit()

        # 不再调用 Docker 工具创建容器，只保存数据库
        return jsonify({"success": True, "message": f"Container {container_name} created successfully in the database"}), 201

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
