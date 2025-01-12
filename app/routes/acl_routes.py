from flask import Blueprint, request, jsonify
from app.models import ACLLog, User, Server, DockerContainer, ACLConfig
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
import os
import json
import logging

# 定义蓝图
acl_bp = Blueprint('acl', __name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
        "derpMap": {
            "OmitDefaultRegions": True,
            "Regions": {}
        }
    }

    for container in containers:
        server = server_info.get(container.server_id)
        if server:
            # 获取地区和相关信息
            region_name = server.region
            region_code = region_name[:2].upper()  # 城市名的声母，例如：上海 -> SH
            region_name_full = region_code.lower() + "derper"  # 如：SZ -> szderper

            # 修正容器节点名称：城市名的声母 + linuxserver
            container_node_name = f"{region_code.lower()}linuxserver"  # 使用城市声母+linuxserver，例如：szlinuxserver

            derp_port = container.port  # 获取容器的端口
            ipv4 = server.ip_address  # 获取服务器的 IP 地址

            # 将 RegionID 改为数字，例如 901
            region_id = 901  # 假设 901 对应于深圳

            # 构建 `derpMap` 和 `Regions` 的结构
            if region_id not in access_control_code["derpMap"]["Regions"]:
                access_control_code["derpMap"]["Regions"][str(region_id)] = {
                    "RegionID": region_id,  # 使用数字作为 RegionID
                    "RegionCode": region_code,
                    "RegionName": region_name_full,
                    "Nodes": []
                }

            # 添加新的节点
            access_control_code["derpMap"]["Regions"][str(region_id)]["Nodes"].append({
                "Name": container_node_name,
                "RegionID": region_id,
                "DERPPort": derp_port,
                "ipv4": ipv4,
                "InsecureForTests": True  # 保证格式正确
            })

    # 生成带逗号的完整 JSON 字符串（模拟格式）
    json_string = json.dumps(access_control_code, separators=(',', ': '), ensure_ascii=False)

    # 存储或更新 ACL 配置到数据库
    acl_config = ACLConfig.query.filter_by(user_id=user.id).first()
    if acl_config:
        # 更新现有的 ACL 配置
        acl_config.acl_data = json_string  # 更新 ACL 配置数据
        acl_config.version = "v1.0"  # 更新版本号
        acl_config.is_active = True  # 确保该配置仍然有效
        db.session.commit()
    else:
        # 创建新的 ACL 配置
        new_acl_config = ACLConfig(
            user_id=user.id,
            server_ids=json.dumps([server.id for server in servers]),
            container_ids=json.dumps([container.id for container in containers]),
            acl_data=json_string,
            version="v1.0",
            is_active=True
        )
        db.session.add(new_acl_config)
        db.session.commit()

    # 记录 ACL 日志，将 acl_version 放到 details 中
    acl_log = ACLLog(
        user_id=user.id,
        ip_address=request.remote_addr,
        location="Unknown",  # 可用外部服务获取用户地理位置
        details=f"acl_version: v1.0 - ACL generated for user {user.username}"  # 将 acl_version 放到 details 字段
    )
    db.session.add(acl_log)
    db.session.commit()

    # 记录操作日志
    log_operation(user_id=user.id, operation="generate_acl", status="success", details=f"ACL generated for user {user.username}")
    
    # 发送通知邮件，将 ACL 配置内容通过邮件发送
    logging.info(f"Sending email to {user.email}")
    send_notification_email(
        user.email, 
        "Tailscale ACL Generated", 
        f"Your Tailscale Access Control configuration has been successfully generated.\n\n"
        f"Here is your ACL configuration:\n\n{json_string}"  # 将 JSON 字符串作为邮件内容
    )
    
    # 打印日志
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
    container_ids = data.get('container_ids')

    # 检查必需字段
    if not user_id or not server_ids or not container_ids:
        log_operation(user_id=None, operation="update_acl", status="failed", details="Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 查询用户的 ACL 配置
    acl_config = ACLConfig.query.filter_by(user_id=user_id).first()
    if not acl_config:
        log_operation(user_id=user_id, operation="update_acl", status="failed", details="No existing ACL configuration")
        return jsonify({"success": False, "message": "No existing ACL configuration for this user"}), 404

    # 获取服务器信息（包括地区信息）
    servers = Server.query.filter(Server.id.in_(server_ids)).all()
    if not servers:
        log_operation(user_id=user_id, operation="update_acl", status="failed", details="Invalid server IDs")
        return jsonify({"success": False, "message": "Invalid server IDs"}), 404

    # 获取容器信息
    containers = DockerContainer.query.filter(DockerContainer.id.in_(container_ids)).all()
    if not containers:
        log_operation(user_id=user_id, operation="update_acl", status="failed", details="No containers found")
        return jsonify({"success": False, "message": "No containers found"}), 404

    # 更新 Tailscale Access Control 配置代码
    access_control_code = {
        "user_id": user_id,
        "username": acl_config.username,
        "email": acl_config.email,
        "derpMap": {
            "OmitDefaultRegions": True,
            "Regions": {}
        }
    }

    # 获取服务器信息并填充到 ACL 配置中
    for container in containers:
        server = next((s for s in servers if s.id == container.server_id), None)
        if server:
            region_name = server.region
            region_code = region_name[:2].upper()  # 城市名的声母，例如：深圳 -> SZ
            region_name_full = region_code.lower() + "derper"  # 如：SZ -> szderper

            container_node_name = region_code.lower() + container.container_name[2:]  # 生成容器节点名称，如：hklinuxserver -> szlinuxserver

            derp_port = container.port  # 获取容器的端口
            ipv4 = server.ip_address  # 获取服务器的 IP 地址

            region_id = 901  # 假设 901 对应于深圳

            if region_id not in access_control_code["derpMap"]["Regions"]:
                access_control_code["derpMap"]["Regions"][str(region_id)] = {
                    "RegionID": region_id,
                    "RegionCode": region_code,
                    "RegionName": region_name_full,
                    "Nodes": []
                }

            # 添加新的节点（手动加逗号）
            access_control_code["derpMap"]["Regions"][str(region_id)]["Nodes"].append({
                "Name": container_node_name,
                "RegionID": region_id,
                "DERPPort": derp_port,
                "ipv4": ipv4,
                "InsecureForTests": True
            })

    # 更新数据库中的 ACL 配置
    acl_config.server_ids = json.dumps([server.id for server in servers])
    acl_config.container_ids = json.dumps([container.id for container in containers])
    acl_config.acl_data = json.dumps(access_control_code)
    acl_config.version = "v1.1"  # 更新版本号
    acl_config.is_active = True  # 确保该配置仍然有效

    db.session.commit()

    # 记录 ACL 日志，将 acl_version 放到 details 中
    acl_log = ACLLog(
        user_id=user.id,
        ip_address=request.remote_addr,
        location="Unknown",  # 可用外部服务获取用户地理位置
        details=f"acl_version: v1.0 - ACL generated for user {user.username}"  # 将 acl_version 放到 details 字段
    )
    db.session.add(acl_log)
    db.session.commit()

    # 记录操作日志
    log_operation(user_id=user_id, operation="update_acl", status="success", details=f"ACL updated for user {acl_config.username}")

    # 发送通知邮件
    send_notification_email(acl_config.email, "Tailscale ACL Updated", f"Your Tailscale Access Control configuration has been successfully updated.")
    
    # 打印日志
    logging.info(f"Tailscale ACL updated for user {acl_config.username}")

    return jsonify({"success": True, "message": "Tailscale ACL updated successfully", "acl": access_control_code}), 200


# 查询用户 ACL 配置历史
@acl_bp.route('/api/acl/logs/<int:user_id>', methods=['GET'])
def get_acl_logs(user_id):
    """
    获取用户的 Tailscale ACL 配置历史
    """
    try:
        logs = ACLLog.query.filter_by(user_id=user_id).all()  # 查询该用户的所有 ACL 日志
        if not logs:
            return jsonify({"success": False, "message": "No ACL logs found"}), 404

        log_data = [
            {
                "ip_address": log.ip_address,
                "location": log.location,
                "acl_version": log.acl_version,
                "created_at": log.created_at  # 返回日志的创建时间
            } for log in logs
        ]

        return jsonify({"success": True, "logs": log_data}), 200  # 返回成功的响应和日志数据

    except Exception as e:
        # 处理查询过程中可能出现的异常
        logging.error(f"Error retrieving ACL logs for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error retrieving ACL logs: {str(e)}"}), 500


# 提供 ACL 文件下载
@acl_bp.route('/api/acl/download/<username>', methods=['GET'])
def download_acl(username):
    """
    提供用户的 Tailscale ACL 文件下载
    """
    try:
        acl_config = ACLConfig.query.filter_by(user_id=username).first()  # 查询该用户的 ACL 配置
        if not acl_config:
            return jsonify({"success": False, "message": "Tailscale ACL not found for this user"}), 404

        acl_data = json.loads(acl_config.acl_data)  # 解析存储的 ACL 数据

        # 构造返回的 JSON 格式的 ACL 配置
        return jsonify({"success": True, "acl": acl_data}), 200

    except Exception as e:
        logging.error(f"Error downloading Tailscale ACL for user {username}: {str(e)}")
        return jsonify({"success": False, "message": f"Error downloading Tailscale ACL: {str(e)}"}), 500
