from flask import Blueprint, request, jsonify
from app.models import UserContainer, User, Server
from app.utils.docker_utils import create_container, stop_container
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
        return jsonify({"success": False, "message": "Invalid user or server ID"}), 404

    # 创建容器
    container_name = f"container_{user.id}_{server.id}"
    image = "derp-container-image"  # 替换为实际镜像名称
    ports = {f"{port}/tcp": port, f"{stun_port}/udp": stun_port}
    container = create_container(image=image, name=container_name, ports=ports)

    if not container:
        return jsonify({"success": False, "message": "Failed to create container"}), 500

    # 保存到数据库
    user_container = UserContainer(
        user_id=user.id,
        server_id=server.id,
        port=port,
        stun_port=stun_port,
    )
    db.session.add(user_container)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Container allocated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 查看容器状态
@container_bp.route('/api/container/status/<int:container_id>', methods=['GET'])
def container_status(container_id):
    """
    查看容器状态
    """
    container = UserContainer.query.get(container_id)

    if not container:
        return jsonify({"success": False, "message": "Container not found"}), 404

    return jsonify({
        "success": True,
        "container": {
            "id": container.id,
            "user_id": container.user_id,
            "server_id": container.server_id,
            "port": container.port,
            "stun_port": container.stun_port,
            "upload_traffic": container.upload_traffic,
            "download_traffic": container.download_traffic,
        }
    }), 200


# 释放容器
@container_bp.route('/api/container/release/<int:container_id>', methods=['DELETE'])
def release_container(container_id):
    """
    释放容器资源
    """
    container = UserContainer.query.get(container_id)

    if not container:
        return jsonify({"success": False, "message": "Container not found"}), 404

    try:
        stop_container(container_id)
        db.session.delete(container)
        db.session.commit()
        return jsonify({"success": True, "message": "Container released successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Failed to release container: {str(e)}"}), 500
