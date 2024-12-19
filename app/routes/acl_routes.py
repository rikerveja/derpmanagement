from flask import Blueprint, request, jsonify, send_file
from app.models import User, Server
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
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
        log_operation(user_id=None, operation="generate_acl", status="failed", details="Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    servers = Server.query.filter(Server.id.in_(server_ids)).all()

    if not user or not servers:
        log_operation(user_id=user_id, operation="generate_acl", status="failed", details="Invalid user or server IDs")
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

    log_operation(user_id=user.id, operation="generate_acl", status="success", details=f"ACL generated for user {user.username}")
    send_notification_email(user.email, "ACL Generated", f"Your ACL configuration has been successfully generated.")
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
        log_operation(user_id=None, operation="update_acl", status="failed", details="Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if user_id not in acl_store:
        log_operation(user_id=user_id, operation="update_acl", status="failed", details="No existing ACL configuration")
        return jsonify({"success": False, "message": "No existing ACL configuration for this user"}), 404

    servers = Server.query.filter(Server.id.in_(server_ids)).all()
    if not servers:
        log_operation(user_id=user_id, operation="update_acl", status="failed", details="Invalid server IDs")
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

    log_operation(user_id=user.id, operation="update_acl", status="success", details=f"ACL updated for user {user.username}")
    send_notification_email(user.email, "ACL Updated", f"Your ACL configuration has been successfully updated.")
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
        log_operation(user_id=user_id, operation="get_acl_history", status="failed", details="No ACL configuration found")
        return jsonify({"success": False, "message": "No ACL configuration found for this user"}), 404

    log_operation(user_id=user_id, operation="get_acl_history", status="success", details="ACL configuration retrieved")
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
        log_operation(user_id=None, operation="download_acl", status="failed", details=f"ACL file for {username} not found")
        return jsonify({"success": False, "message": "ACL file not found"}), 404

    try:
        log_operation(user_id=None, operation="download_acl", status="success", details=f"ACL file downloaded for {username}")
        logging.info(f"ACL file for user {username} downloaded")
        return send_file(acl_file_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading ACL file for user {username}: {e}")
        log_operation(user_id=None, operation="download_acl", status="failed", details=f"Error downloading ACL: {str(e)}")
        return jsonify({"success": False, "message": f"Error downloading ACL: {str(e)}"}), 500


# 验证用户对服务器的权限
@acl_bp.route('/api/acl/validate', methods=['POST'])
def validate_acl():
    """
    验证用户对指定服务器的访问权限
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    acl_config = acl_store.get(user_id)
    if not acl_config:
        log_operation(user_id=user_id, operation="validate_acl", status="failed", details="No ACL configuration found")
        return jsonify({"success": False, "message": "No ACL configuration found for this user"}), 404

    server_access = any(server['id'] == server_id for server in acl_config['servers'])
    if server_access:
        log_operation(user_id=user_id, operation="validate_acl", status="success", details=f"Access granted to server {server_id}")
        return jsonify({"success": True, "message": "Access granted"}), 200
    log_operation(user_id=user_id, operation="validate_acl", status="failed", details=f"Access denied to server {server_id}")
    return jsonify({"success": False, "message": "Access denied"}), 403
