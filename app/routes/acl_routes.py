from flask import Blueprint, request, jsonify 
from app.models import ACLLog, User, Server, DockerContainer, ACLConfig
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
import json
import logging
import os

# 定义蓝图
acl_bp = Blueprint('acl', __name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 城市映射表，提供城市名到拼音和代码的映射
CITY_NAME_MAPPING = {
    "长沙": {"region_code": "CS", "region_name_full": "changsha"},
    "上海": {"region_code": "SH", "region_name_full": "shanghai"},
    "深圳": {"region_code": "SZ", "region_name_full": "shenzhen"},
    "广州": {"region_code": "GZ", "region_name_full": "guangzhou"},
    "北京": {"region_code": "BJ", "region_name_full": "beijing"},
    "杭州": {"region_code": "HZ", "region_name_full": "hangzhou"},
    "成都": {"region_code": "CD", "region_name_full": "chengdu"},
    "武汉": {"region_code": "WH", "region_name_full": "wuhan"},
    "天津": {"region_code": "TJ", "region_name_full": "tianjin"},
    "重庆": {"region_code": "CQ", "region_name_full": "chongqing"},
    "西安": {"region_code": "XA", "region_name_full": "xian"},
    "青岛": {"region_code": "QD", "region_name_full": "qingdao"},
    "南京": {"region_code": "NJ", "region_name_full": "nanjing"},
}

@acl_bp.route('/api/acl/configs', methods=['GET'])
def get_acl_configs():
    """
    获取 ACL 配置的列表，返回字段：用户、服务器、容器、版本、状态、更新时间、操作、以及格式化的 derpMap 结构。
    """
    try:
        # 查询 ACLConfig 表中的所有记录
        acl_configs = ACLConfig.query.all()
        
        # 格式化查询结果
        acl_configs_list = []
        
        for acl in acl_configs:
            # 获取关联的用户信息
            user = User.query.get(acl.user_id)
            if not user:
                continue  # 如果用户不存在，跳过当前记录
            
            # 获取关联的服务器信息
            servers = Server.query.filter(Server.id.in_(acl.server_ids)).all()
            server_info = [{"id": server.id, "ip_address": server.ip_address, "region": server.region} for server in servers]

            # 获取关联的容器信息
            containers = DockerContainer.query.filter(DockerContainer.id.in_(acl.container_ids)).all()
            container_info = [{"id": container.id, "name": container.container_name, "port": container.port, "status": container.status} for container in containers]

            # 格式化 derpMap 结构
            access_control_code = json.loads(acl.acl_data)  # 解析存储的 ACL 数据
            derp_map = format_derp_map(access_control_code)

            # 构建 ACL 配置的返回信息
            acl_config_data = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "servers": server_info,
                "containers": container_info,
                "version": acl.version,
                "is_active": acl.is_active,
                "created_at": acl.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间
                "updated_at": acl.updated_at.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间
                "operation": "Updated" if acl.updated_at != acl.created_at else "Created",
                "derpMap": derp_map  # 返回格式化后的 derpMap 结构
            }
            
            acl_configs_list.append(acl_config_data)

        # 返回成功的响应和 ACL 配置列表
        return jsonify({"success": True, "acl_configs": acl_configs_list}), 200

    except Exception as e:
        # 处理可能出现的异常
        return jsonify({"success": False, "message": f"Error retrieving ACL configs: {str(e)}"}), 500

def format_derp_map(access_control_code):
    """
    格式化 derpMap 为前端显示用的格式（例如添加逗号、移除大括号等）
    """
    # 格式化 derpMap 字段的输出
    json_string = json.dumps(access_control_code, ensure_ascii=False, indent=4)
    json_string = json_string[1:-2]  # 去掉最外层的大括号 {} 和最后的逗号
    json_string = json_string.replace("}", "},").replace("]", "],").rstrip(",") + ","
    return json_string

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
        },
    }

    for container in containers:
        server = server_info.get(container.server_id)
        if server:
            # 从映射表中获取城市代码和拼音
            city_info = CITY_NAME_MAPPING.get(server.region, {"region_code": "UNKNOWN", "region_name_full": server.region.lower()})
            region_code = city_info["region_code"]  # 城市代码
            region_name_full = f"{city_info['region_name_full']}derper"  # 拼音全拼 + derper

            # 修正容器节点名称：城市代码 + linuxserver
            container_node_name = f"{region_code.lower()}linuxserver"

            derp_port = container.port  # 获取容器的端口
            ipv4 = server.ip_address  # 获取服务器的 IP 地址

            # 假设 region_id 是从服务器表中得来的
            region_id = 901  # 示例固定值 901

            # 构建 derpMap 和 Regions 的结构
            if str(region_id) not in access_control_code["derpMap"]["Regions"]:
                access_control_code["derpMap"]["Regions"][str(region_id)] = {
                    "RegionID": region_id,
                    "RegionCode": region_code,  # 使用映射表中的城市代码
                    "RegionName": region_name_full,  # 使用映射表中的拼音全拼
                    "Nodes": [],
                }

            # 添加新的节点
            access_control_code["derpMap"]["Regions"][str(region_id)]["Nodes"].append({
                "Name": container_node_name,
                "RegionID": region_id,
                "DERPPort": derp_port,
                "ipv4": ipv4,
                "InsecureForTests": True,
            })

    # 标准 JSON 数据（存储到数据库）
    database_json = json.dumps(access_control_code, ensure_ascii=False)

    # 格式化邮件用的 JSON（添加多余的逗号等）
    def format_nonstandard_json(data):
        json_string = json.dumps(data, ensure_ascii=False, indent=4)
        json_string = json_string[1:-2]  # 去掉最外层的大括号 {} 和最后的逗号
        json_string = json_string.replace("}", "},").replace("]", "],").rstrip(",") + ","
        return json_string

    email_json = format_nonstandard_json(access_control_code)

    # 存储或更新 ACL 配置到数据库
    acl_config = ACLConfig.query.filter_by(user_id=user.id).first()
    try:
        if acl_config:
            # 更新现有的 ACL 配置
            acl_config.server_ids = [server.id for server in servers]  # 存储数组而非 JSON 字符串
            acl_config.container_ids = [container.id for container in containers]
            acl_config.acl_data = database_json  # 存储标准 JSON 对象
            acl_config.version = "v1.0"
            acl_config.is_active = True
        else:
            # 创建新的 ACL 配置
            acl_config = ACLConfig(
                user_id=user.id,
                server_ids=[server.id for server in servers],  # 存储数组而非 JSON 字符串
                container_ids=[container.id for container in containers],
                acl_data=database_json,  # 存储标准 JSON 对象
                version="v1.0",
                is_active=True,
            )
            db.session.add(acl_config)

        db.session.commit()  # 提交事务
    except Exception as e:
        db.session.rollback()  # 发生错误时回滚事务
        logging.error(f"Failed to insert or update ACLConfig: {e}")
        return jsonify({"success": False, "message": "Database operation failed"}), 500

    # 记录 ACL 日志
    acl_log = ACLLog(
        user_id=user.id,
        ip_address=request.remote_addr,
        location="Unknown",
        details=f"acl_version: v1.0 - ACL generated for user {user.username}",
    )
    db.session.add(acl_log)
    db.session.commit()

    # 记录操作日志
    log_operation(user_id=user.id, operation="generate_acl", status="success", details=f"ACL generated for user {user.username}")

    # 发送通知邮件
    send_notification_email(
        user.email,
        "Tailscale ACL Generated",
        f"Your Tailscale Access Control configuration has been successfully generated.\n\n"
        f"Here is your ACL configuration:\n\n{email_json}",
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


# 提供 ACL 配置数据接口
@acl_bp.route('/api/acl/download/<user_id>', methods=['GET'])
def download_acl(user_id):
    """
    从数据库获取用户的 Tailscale ACL 配置并返回
    """
    try:
        # 从数据库中获取 ACL 配置数据
        acl_config = ACLConfig.query.filter_by(user_id=user_id).first()  # 根据 user_id 查询 ACL 配置
        if not acl_config:
            return jsonify({"success": False, "message": "Tailscale ACL not found for this user"}), 404

        # 解析存储的 acl_data 数据
        acl_data = json.loads(acl_config.acl_data)  # 将字符串格式的 JSON 数据转化为 Python 字典

        # 格式化数据并准备返回
        formatted_acl_data = format_acl_data(acl_data)

        # 返回格式化后的数据
        return jsonify({"success": True, "acl": formatted_acl_data}), 200

    except Exception as e:
        logging.error(f"Error downloading Tailscale ACL for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error downloading Tailscale ACL: {str(e)}"}), 500

def format_acl_data(acl_data):
    """
    格式化 ACL 数据，将其转换为符合要求的结构
    """
    # 这里您可以根据需要进一步处理和格式化 ACL 数据
    formatted_data = {
        "version": acl_data.get("version", ""),
        "acl": {
            "allow": acl_data.get("allow", []),
            "deny": acl_data.get("deny", [])
        },
        "tags": acl_data.get("tags", {}),
        "groups": acl_data.get("groups", {}),
    }
    return formatted_data

