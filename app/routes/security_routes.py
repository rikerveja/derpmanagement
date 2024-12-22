from flask import Blueprint, jsonify, request
from app.models import User, ACLConfig, Server, UserContainer, db
import logging

# 定义蓝图
security_bp = Blueprint('security', __name__)
logging.basicConfig(level=logging.INFO)

@security_bp.route('/api/security/user_acl_info/<int:user_id>', methods=['GET'])
def get_user_acl_info(user_id):
    """
    获取用户对应的 ACL 配置信息，包括服务器公网 IP、服务器信息、Docker 容器和 DERP 服务端口号
    """
    try:
        # 查询用户的 ACL 配置
        acl_configs = ACLConfig.query.filter_by(user_id=user_id).all()
        if not acl_configs:
            logging.error(f"No ACL configs found for user {user_id}")
            return jsonify({"success": False, "message": "No ACL config found for this user"}), 404

        result = []
        for acl_config in acl_configs:
            # 获取服务器信息
            server = acl_config.server
            container = acl_config.container
            derp_port = acl_config.derp_port

            result.append({
                "server_ip": server.ip,  # 服务器公网 IP
                "server_region": server.region,  # 服务器区域
                "server_status": server.status,  # 服务器状态
                "container_name": container.name,  # 容器名称
                "derp_port": derp_port,  # DERP 服务端口号
                "container_status": container.status,  # 容器状态
            })

        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        logging.error(f"Error fetching ACL information for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching ACL information: {str(e)}"}), 500
