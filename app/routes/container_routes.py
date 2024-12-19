from flask import Blueprint, request, jsonify
from app.models import UserContainer, User, Server
from app import db

container_bp = Blueprint('container', __name__)

# 添加用户容器
@container_bp.route('/api/add_user_container', methods=['POST'])
def add_user_container():
    """
    添加用户容器
    请求参数:
        - user_id: 用户 ID
        - server_id: 服务器 ID
        - port: DERP 端口
        - stun_port: STUN 端口
    返回:
        - 成功或失败信息
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')
    port = data.get('port')
    stun_port = data.get('stun_port')

    # 检查请求参数是否完整
    if not all([user_id, server_id, port, stun_port]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 检查用户和服务器是否存在
    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if not server:
        return jsonify({"success": False, "message": "Server not found"}), 404

    # 检查端口是否冲突
    existing_container = UserContainer.query.filter_by(server_id=server_id, port=port).first()
    if existing_container:
        return jsonify({"success": False, "message": "Port already in use on this server"}), 400

    # 创建用户容器
    container = UserContainer(user_id=user_id, server_id=server_id, port=port, stun_port=stun_port)
    db.session.add(container)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User container added successfully", "container_id": container.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
