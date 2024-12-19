from flask import Blueprint, request, jsonify
from app.models import User, Server
from app import db
import logging
import json

# 定义蓝图
acl_bp = Blueprint('acl', __name__)
logging.basicConfig(level=logging.INFO)

# 模拟存储 ACL 配置
acl_store = {}

# 生成 ACL 配置
@acl_bp.route('/api/acl/generate', methods=['POST'])
def generate_acl():
    """
    动态生成 ACL 配置
    """
    data = request.json
    user_id = data.get('user_id')
    server_ids = data.get('server_ids')

    if not user_id or not server_ids:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    servers = Server.query.filter(Server.id.in_(server_ids)).all()

    if not user or not servers:
        return jsonify({"success": False, "message": "Invalid user or server IDs"}), 404

    # 动态生成 ACL 配置
    acl_config = {
        "user_id": user.id,
        "servers": [{"id": server.id, "ip": server.ip, "region": server.region} for server in servers]
    }
    acl_store[user.id] = acl_config  # 模拟存储 ACL 配置

    return jsonify({"success": True, "message": "ACL generated successfully", "acl": acl_config}), 200


# 更新 ACL 配置
@acl_bp.route('/api/acl/update', methods=['POST'])
def update_acl():
    """
    手动更新 ACL 配置
    """
    data = request.json
    user_id = data.get('user_id')
    server_ids = data.get('server_ids')

    if not user_id or not server_ids:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if user_id not in acl_store:
        return jsonify({"success": False, "message": "No existing ACL configuration for this user"}), 404

    servers = Server.query.filter(Server.id.in_(server_ids)).all()
    if not servers:
        return jsonify({"success": False, "message": "Invalid server IDs"}), 404

    # 更新 ACL 配置
    acl_config = {
        "user_id": user_id,
        "servers": [{"id": server.id, "ip": server.ip, "region": server.region} for server in servers]
    }
    acl_store[user_id] = acl_config

    return jsonify({"success": True, "message": "ACL updated successfully", "acl": acl_config}), 200


# 获取 ACL 配置历史
@acl_bp.route('/api/acl/history/<int:user_id>', methods=['GET'])
def get_acl_history(user_id):
    """
    查询用户 ACL 配置历史
    """
    acl_config = acl_store.get(user_id)

    if not acl_config:
        return jsonify({"success": False, "message": "No ACL configuration found for this user"}), 404

    return jsonify({"success": True, "acl": acl_config}), 200
