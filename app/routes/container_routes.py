from flask import Blueprint, request, jsonify
from app.models import UserContainer, User, Server
from app.utils.docker_utils import create_container, stop_container, get_container_status, list_containers
from app import db

container_bp = Blueprint('container', __name__)

# 动态分配容器
@container_bp.route('/api/container/allocate', methods=['POST'])
def allocate_container():
    """
    为用户动态分配容器
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')
    port = data.get('port')
    stun_port = data.get('stun_port')

    if not user_id or not server_id or not port or not stun_port:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    # 创建 Docker 容器
    container_name = f"user_{user_id}_container"
    image = "your_docker_image"  # 替换为实际的 Docker 镜像名称
    ports = {'80/tcp': port, '3478/udp': stun_port}
    environment = {'USER_ID': user_id}

    container = create_container(image, container_name, ports, environment)

    if container is None:
        return jsonify({"success": False, "message": "Failed to create container"}), 500

    # 在数据库中记录
    user_container = UserContainer(
        user_id=user_id,
        server_id=server_id,
        port=port,
        stun_port=stun_port
    )
    db.session.add(user_container)
    db.session.commit()

    return jsonify({"success": True, "message": "Container allocated successfully"}), 201

# 停止并删除容器
@container_bp.route('/api/container/deallocate', methods=['POST'])
def deallocate_container():
    """
    停止并删除用户的容器
    """
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id"}), 400

    user_container = UserContainer.query.filter_by(user_id=user_id).first()

    if not user_container:
        return jsonify({"success": False, "message": "User container not found"}), 404

    container_name = f"user_{user_id}_container"

    # 停止并删除 Docker 容器
    stop_container(container_name)

    # 从数据库中删除记录
    db.session.delete(user_container)
    db.session.commit()

    return jsonify({"success": True, "message": "Container deallocated successfully"}), 200

# 获取容器状态
@container_bp.route('/api/container/status/<int:user_id>', methods=['GET'])
def container_status(user_id):
    """
    获取用户容器的状态
    """
    container_name = f"user_{user_id}_container"
    status = get_container_status(container_name)

    if status is None:
        return jsonify({"success": False, "message": "Container not found"}), 404

    return jsonify({"success": True, "status": status}), 200

# 列出所有容器
@container_bp.route('/api/container/list', methods=['GET'])
def list_all_containers():
    """
    列出所有容器
    """
    containers = list_containers(all=True)
    return jsonify({"success": True, "containers": containers}), 200
