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

# 动态生成 Tailscale Access Control 配置
@acl_bp.route('/api/acl/generate', methods=['POST'])
def generate_acl():
    """
    动态生成用户的 Tailscale Access Control 配置代码
    """
    data = request.json
    user_id = data.get('user_id')
    server_ids = data.get('server_ids')

    # 检查必需字段
    if not user_id or not server_ids:
        log_operation(user_id=None, operation="generate_acl", status="failed", details="Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        log_operation(user_id=user_id, operation="generate_acl", status="failed", details="User not found")
        return jsonify({"success": False, "message": "User not found"}), 404

    servers = Server.query.filter(Server.id.in_(server_ids)).all()
    if not servers:
        log_operation(user_id=user_id, operation="generate_acl", status="failed", details="Invalid server IDs")
        return jsonify({"success": False, "message": "Invalid server IDs"}), 404

    # 动态生成 Tailscale Access Control 配置代码
    access_control_code = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "access_controls": [
            {
                "action": "accept",
                "ip": server.ip,
                "ports": "80,443"  # 假设只开放 HTTP/HTTPS 端口，可以根据实际需要修改
            }
            for server in servers
        ]
    }

    # 存储或更新 ACL 配置
    acl_store[user.id] = access_control_code
    acl_file_path = f"acl_files/{user.username}_tailscale_acl.json"
    os.makedirs("acl_files", exist_ok=True)
    with open(acl_file_path, "w") as acl_file:
        json.dump(access_control_code, acl_file)

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
    send_notification_email(user.email, "Tailscale ACL Generated", f"Your Tailscale Access Control configuration has been successfully generated.")
    logging.info(f"Tailscale ACL generated for user {user.username}")

    return jsonify({"success": True, "message": "Tailscale ACL generated successfully", "acl": access_control_code}), 200


# 手动更新 ACL 配置
@acl_bp.route('/api/acl/update', methods=['POST'])
def update_acl():
    """
    手动更新用户的 Tailscale Access Control 配置
    """
    data = request.json
    user_id = data.get('user_id')
    server_ids = data.get('server_ids')

    # 检查必需字段
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

    # 更新 Tailscale Access Control 配置代码
    user = User.query.get(user_id)
    access_control_code = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "access_controls": [
            {
                "action": "accept",
                "ip": server.ip,
                "ports": "80,443"  # 根据实际需求调整
            }
            for server in servers
        ]
    }

    acl_store[user.id] = access_control_code
    acl_file_path = f"acl_files/{user.username}_tailscale_acl.json"
    with open(acl_file_path, "w") as acl_file:
        json.dump(access_control_code, acl_file)

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
    send_notification_email(user.email, "Tailscale ACL Updated", f"Your Tailscale Access Control configuration has been successfully updated.")
    logging.info(f"Tailscale ACL updated for user {user.username}")

    return jsonify({"success": True, "message": "Tailscale ACL updated successfully", "acl": access_control_code}), 200


# 查询用户 ACL 配置历史
@acl_bp.route('/api/acl/logs/<int:user_id>', methods=['GET'])
def get_acl_logs(user_id):
    """
    获取用户的 Tailscale ACL 配置历史
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

    log_operation(user_id=user_id, operation="get_acl_logs", status="success", details="Tailscale ACL logs retrieved")
    return jsonify({"success": True, "logs": log_data}), 200


# 提供 ACL 文件下载
@acl_bp.route('/api/acl/download/<username>', methods=['GET'])
def download_acl(username):
    """
    提供用户的 Tailscale ACL 文件下载
    """
    acl_file_path = f"acl_files/{username}_tailscale_acl.json"
    if not os.path.exists(acl_file_path):
        logging.error(f"Tailscale ACL file for user {username} not found")
        log_operation(user_id=None, operation="download_acl", status="failed", details=f"Tailscale ACL file for {username} not found")
        return jsonify({"success": False, "message": "Tailscale ACL file not found"}), 404

    try:
        log_operation(user_id=None, operation="download_acl", status="success", details=f"Tailscale ACL file downloaded for {username}")
        logging.info(f"Tailscale ACL file for user {username} downloaded")
        return send_file(acl_file_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading Tailscale ACL file for user {username}: {e}")
        log_operation(user_id=None, operation="download_acl", status="failed", details=f"Error downloading Tailscale ACL: {str(e)}")
        return jsonify({"success": False, "message": f"Error downloading Tailscale ACL: {str(e)}"}), 500
