from flask import Blueprint, request, jsonify
from app.models import UserContainer, User, Server
from app import db

container_bp = Blueprint('container', __name__)

# 添加用户容器
@container_bp.route('/api/add_user_container', methods=['POST'])
def add_user_container():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')
    port = data.get('port')
    stun_port = data.get('stun_port')

    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    existing_container = UserContainer.query.filter_by(server_id=server_id, port=port).first()
    if existing_container:
        return jsonify({"success": False, "message": "Port already in use on this server"}), 400

    container = UserContainer(user_id=user_id, server_id=server_id, port=port, stun_port=stun_port)
    db.session.add(container)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User container added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
