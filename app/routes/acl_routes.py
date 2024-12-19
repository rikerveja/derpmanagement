from flask import Blueprint, request, jsonify, send_file
from app.models import User, Server
from app import db
import logging
import os
import json

# 定义蓝图
acl_bp = Blueprint('acl', __name__)
logging.basicConfig(level=logging.INFO)

# 模拟存储 ACL 配置（临时存储，可以替换为数据库存储）
acl_store = {}

# 动态生成 ACL 配置
@acl_bp.route('/api/acl/generate', methods=['POST'])
def generate_acl():
    """
    动态生成用户 ACL 配置
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
        "username": user.username,
        "email": user.email,
        "servers": [{"id": server.id, "ip": server.ip, "region": server.region} for server in servers]
    }

    # 保存到临时存储或文件
    acl_store[user.id] = acl_config
    acl_file_path = f"acl_files/{user.username}_acl.json"
    os.makedirs("acl_files", exist_ok=True)
    with open(acl_file_path, "w") as acl_file:
        json.dump(acl_config, acl_file)

    logging.info(f"ACL generated for user {user.username}")
    return jsonify({"success": True, "message": "ACL generated successfully", "acl": acl_config}), 200


# 手动更新 ACL 配置
@acl_bp.route('/api/acl/update', methods=['POST'])
def update_acl():
    """
    手动更新用户 ACL 配置
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
    user = User.query.get(user_id)
    acl_config = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "servers": [{"id": server.id, "ip": server.ip, "region": server.region} for server in servers]
    }

    acl_store[user.id] = acl_config
    acl_file_path = f"acl_files/{user.username}_acl.json"
    with open(acl_file_path, "w") as acl_file:
        json.dump(acl_config, acl_file)

    logging.info(f"ACL updated for user {user.username}")
    return jsonify({"success": True, "message": "ACL updated successfully", "acl": acl_config}), 200


# 查询用户 ACL 配置历史
@acl_bp.route('/api/acl/history/<int:user_id>', methods=['GET'])
def get_acl_history(user_id):
    """
    获取用户 ACL 配置历史
    """
    acl_config = acl_store.get(user_id)

    if not acl_config:
        return jsonify({"success": False, "message": "No ACL configuration found for this user"}), 404

    return jsonify({"success": True, "acl": acl_config}), 200


# 提供 ACL 文件下载
@acl_bp.route('/api/acl/download/<username>', methods=['GET'])
def download_acl(username):
    """
    提供用户 ACL 文件下载
    """
    acl_file_path = f"acl_files/{username}_acl.json"
    if not os.path.exists(acl_file_path):
        logging.error(f"ACL file for user {username} not found")
        return jsonify({"success": False, "message": "ACL file not found"}), 404

    try:
        logging.info(f"ACL file for user {username} downloaded")
        return send_file(acl_file_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading ACL file for user {username}: {e}")
        return jsonify({"success": False, "message": f"Error downloading ACL: {str(e)}"}), 500
