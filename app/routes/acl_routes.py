from flask import Blueprint, request, jsonify, send_file
from app.models import ACLLog, User, Server
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
import os
import json
import logging

# 定义蓝图
acl_bp = Blueprint('acl', __name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

    # 记录 ACL 日志
    acl_log = ACLLog(
        user_id=user.id,
        ip_address=request.remote_addr,
        location="Unknown",  # 可用外部服务获取用户地理位置
        acl_version="v1.0"  # 动态生成 ACL 版本号
    )
    db.session.add(acl_log)
    db.session.commit()

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

    # 记录更新日志
    acl_log = ACLLog(
        user_id=user.id,
        ip_address=request.remote_addr,
        location="Unknown",  # 地理位置可填入实际获取结果
        acl_version="v1.1"  # 新版本号
    )
    db.session.add(acl_log)
    db.session.commit()

    log_operation(user_id=user.id, operation="update_acl", status="success", details=f"ACL updated for user {user.username}")
    send_notification_email(user.email, "ACL Updated", f"Your ACL configuration has been successfully updated.")
    logging.info(f"ACL updated for user {user.username}")

    return jsonify({"success": True, "message": "ACL updated successfully", "acl": acl_config}), 200


# 查询用户 ACL 配置历史
@acl_bp.route('/api/acl/logs/<int:user_id>', methods=['GET'])
def get_acl_logs(user_id):
    """
    获取用户 ACL 配置历史
    """
    logs = ACLLog.query.filter_by(user_id=user_id).all()
    if not logs:
        log_operation(user_id=user_id, operation="get_acl_logs", status="failed", details="No ACL logs found")
        return jsonify({"success": False, "message": "No ACL logs found"}), 404

    log_data = [
        {
            "ip_address": log.ip_address,
            "location": log.location,
            "acl_version": log.acl_version,
            "created_at": log.created_at
        } for log in logs
    ]

    log_operation(user_id=user_id, operation="get_acl_logs", status="success", details="ACL logs retrieved")
    return jsonify({"success": True, "logs": log_data}), 200


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
