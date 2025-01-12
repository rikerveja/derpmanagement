from flask import Blueprint, request, jsonify, send_file
from app.models import ACLLog, User, Server, DockerContainer, ACLConfig
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
import json
import logging

# 定义蓝图
acl_bp = Blueprint('acl', __name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 动态生成 Tailscale Access Control 配置
@acl_bp.route('/api/acl/generate', methods=['POST'])
def generate_acl():
    """
    动态生成用户的 Tailscale Access Control 配置代码
    """
    data = request.json
    user_id = data.get('user_id')
    container_ids = data.get('container_ids')

    # 检查必需字段
    if not user_id or not container_ids:
        log_operation(user_id=None, operation="generate_acl", status="failed", details="Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        log_operation(user_id=user_id, operation="generate_acl", status="failed", details="User not found")
        return jsonify({"success": False, "message": "User not found"}), 404

    # 获取容器信息
    containers = DockerContainer.query.filter(DockerContainer.id.in_(container_ids)).all()
    if not containers:
        log_operation(user_id=user_id, operation="generate_acl", status="failed", details="No containers found")
        return jsonify({"success": False, "message": "No containers found"}), 404

    # 获取服务器信息（包括地区信息）
    server_ids = set([container.server_id for container in containers])
    servers = Server.query.filter(Server.id.in_(server_ids)).all()
    server_info = {server.id: server for server in servers}

    # 动态生成 ACL 配置
    access_control_code = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "access_controls": []
    }

    for container in containers:
        server = server_info.get(container.server_id)
        if server:
            # 根据容器和服务器的特性生成 ACL 配置
            access_control = {
                "action": "accept",
                "ip": container.ip_address,  # 容器的 IP 地址
                "ports": f"{container.port},{container.stun_port}",  # 假设开放 HTTP/HTTPS 和 STUN 端口
                "server_region": server.region  # 服务器地区信息
            }
            access_control_code["access_controls"].append(access_control)

    # 存储或更新 ACL 配置到数据库
    acl_config = ACLConfig.query.filter_by(user_id=user.id).first()
    if acl_config:
        # 更新现有的 ACL 配置
        acl_config.acl_data = json.dumps(access_control_code)  # 更新 ACL 配置数据
        acl_config.version = "v1.0"  # 可以根据需要增加版本号
        acl_config.is_active = True  # 确保该配置仍然有效
        db.session.commit()
    else:
        # 创建新的 ACL 配置
        new_acl_config = ACLConfig(
            user_id=user.id,
            server_ids=json.dumps([server.id for server in servers]),
            container_ids=json.dumps([container.id for container in containers]),
            acl_data=json.dumps(access_control_code),
            version="v1.0",
            is_active=True
        )
        db.session.add(new_acl_config)
        db.session.commit()

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
    container_ids = data.get('container_ids')

    # 检查必需字段
    if not user_id or not container_ids:
        log_operation(user_id=None, operation="update_acl", status="failed", details="Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 获取容器信息
    containers = DockerContainer.query.filter(DockerContainer.id.in_(container_ids)).all()
    if not containers:
        log_operation(user_id=user_id, operation="update_acl", status="failed", details="No containers found")
        return jsonify({"success": False, "message": "No containers found"}), 404

    # 获取服务器信息（包括地区信息）
    server_ids = set([container.server_id for container in containers])
    servers = Server.query.filter(Server.id.in_(server_ids)).all()
    server_info = {server.id: server for server in servers}

    user = User.query.get(user_id)
    access_control_code = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "access_controls": []
    }

    for container in containers:
        server = server_info.get(container.server_id)
        if server:
            access_control = {
                "action": "accept",
                "ip": container.ip_address,
                "ports": f"{container.port},{container.stun_port}",
                "server_region": server.region
            }
            access_control_code["access_controls"].append(access_control)

    # 更新 ACL 配置到数据库
    acl_config = ACLConfig.query.filter_by(user_id=user.id).first()
    if acl_config:
        acl_config.acl_data = json.dumps(access_control_code)
        acl_config.version = "v1.1"  # 更新版本号
        acl_config.is_active = True  # 确保该配置有效
        db.session.commit()
    else:
        new_acl_config = ACLConfig(
            user_id=user.id,
            server_ids=json.dumps([server.id for server in servers]),
            container_ids=json.dumps([container.id for container in containers]),
            acl_data=json.dumps(access_control_code),
            version="v1.1",
            is_active=True
        )
        db.session.add(new_acl_config)
        db.session.commit()

    # 记录更新日志
    acl_log = ACLLog(
        user_id=user.id,
        ip_address=request.remote_addr,
        location="Unknown",  # 地理位置可填入实际获取结果
        acl_version="v1.1"
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
        return jsonify({"success": False, "message": "No ACL logs found"}), 404

    log_data = [
        {
            "ip_address": log.ip_address,
            "location": log.location,
            "acl_version": log.acl_version,
            "created_at": log.created_at
        } for log in logs
    ]

    return jsonify({"success": True, "logs": log_data}), 200


# 提供 ACL 文件下载
@acl_bp.route('/api/acl/download/<username>', methods=['GET'])
def download_acl(username):
    """
    提供用户的 Tailscale ACL 文件下载
    """
    acl_config = ACLConfig.query.filter_by(user_id=username).first()
    if not acl_config:
        return jsonify({"success": False, "message": "Tailscale ACL not found for this user"}), 404

    try:
        acl_data = json.loads(acl_config.acl_data)  # 解析存储的 ACL 数据
        # 构造文件内容或直接返回 JSON 格式的响应
        return jsonify({"success": True, "acl": acl_data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error downloading Tailscale ACL: {str(e)}"}), 500
