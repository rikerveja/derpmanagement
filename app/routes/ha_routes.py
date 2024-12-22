from flask import Blueprint, jsonify, request
import random
from datetime import datetime
from app.utils.logging_utils import log_operation
from app.utils.monitoring_utils import generate_alerts, analyze_server_load, check_server_health
from app.utils.docker_utils import check_docker_health, get_docker_traffic, update_docker_container
from app.models import SystemAlert, Server, User, db
from app.utils.notifications_utils import send_notification_email

# 定义蓝图
ha_bp = Blueprint('ha', __name__)

# 模拟服务器状态
server_health = {
    "server_1": {"status": "healthy", "load": random.uniform(0, 100)},  # 模拟服务器负载
    "server_2": {"status": "healthy", "load": random.uniform(0, 100)},
    "server_3": {"status": "unhealthy", "load": random.uniform(0, 100)}
}

# 查看所有服务器运行状态
@ha_bp.route('/api/ha/health', methods=['GET'])
def check_server_health_status():
    """
    查看所有服务器健康状态
    """
    try:
        return jsonify({"success": True, "server_health": server_health}), 200
    except Exception as e:
        log_operation(user_id=None, operation="check_server_health_status", status="failed", details=f"Error fetching server health: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching server health: {str(e)}"}), 500


# 单个服务器健康检查
@ha_bp.route('/api/ha/health/<server_id>', methods=['GET'])
def check_individual_server_health(server_id):
    """
    查看单个服务器健康状态
    """
    server_info = server_health.get(server_id)
    if not server_info:
        log_operation(user_id=None, operation="check_individual_server_health", status="failed", details="Server not found")
        return jsonify({"success": False, "message": "Server not found"}), 404

    try:
        # 模拟实时检查健康状态（可以改为真实健康检查逻辑）
        server_info['status'] = "healthy" if random.random() > 0.2 else "unhealthy"
        return jsonify({"success": True, "server_id": server_id, "status": server_info['status']}), 200
    except Exception as e:
        log_operation(user_id=None, operation="check_individual_server_health", status="failed", details=f"Error checking server health: {str(e)}")
        return jsonify({"success": False, "message": f"Error checking server health: {str(e)}"}), 500


# 故障切换
@ha_bp.route('/api/ha/failover', methods=['POST'])
def failover():
    """
    故障切换服务到备用服务器
    """
    try:
        unhealthy_servers = [key for key, data in server_health.items() if data['status'] == "unhealthy"]
        if not unhealthy_servers:
            log_operation(user_id=None, operation="failover", status="success", details="No unhealthy servers detected")
            return jsonify({"success": False, "message": "No unhealthy servers detected"}), 200

        # 模拟切换到备用服务器
        for server in unhealthy_servers:
            server_health[server]['status'] = "switched"
            server_health[server]['load'] = 0  # 清空负载

            # 触发告警并通知管理员
            alert = SystemAlert(
                server_id=server,
                alert_type="Server Failure",
                message=f"Server {server} has failed over to a backup server.",
                timestamp=datetime.utcnow(),
                status="active"
            )
            db.session.add(alert)
            db.session.commit()

            # 获取管理员的联系方式并发送邮件
            admins = User.query.filter_by(role="admin").all()
            for admin in admins:
                send_notification_email(admin.email, "Server Failure Notification", f"Server {server} has failed over and is now operating on a backup server.")

        log_operation(user_id=None, operation="failover", status="success", details=f"Failover completed for: {unhealthy_servers}")
        return jsonify({"success": True, "message": "Failover completed", "updated_health": server_health}), 200
    except Exception as e:
        log_operation(user_id=None, operation="failover", status="failed", details=f"Error during failover: {str(e)}")
        return jsonify({"success": False, "message": f"Error during failover: {str(e)}"}), 500


# 负载均衡
@ha_bp.route('/api/ha/load_balance', methods=['POST'])
def load_balance():
    """
    根据服务器负载执行流量重新分配
    """
    data = request.json
    threshold = data.get("threshold", 70)  # 默认负载均衡阈值为 70%

    try:
        high_load_servers = [key for key, data in server_health.items() if data['load'] > threshold]
        if not high_load_servers:
            return jsonify({"success": True, "message": "No servers exceed the load threshold"}), 200

        # 模拟重新分配流量
        for server in high_load_servers:
            server_health[server]['load'] = random.uniform(20, 50)  # 降低高负载服务器的负载

        log_operation(user_id=None, operation="load_balance", status="success", details=f"Load balanced for: {high_load_servers}")
        return jsonify({"success": True, "message": "Load balancing completed", "updated_health": server_health}), 200
    except Exception as e:
        log_operation(user_id=None, operation="load_balance", status="failed", details=f"Error during load balancing: {str(e)}")
        return jsonify({"success": False, "message": f"Error during load balancing: {str(e)}"}), 500


# 灾备恢复
@ha_bp.route('/api/ha/disaster_recovery', methods=['POST'])
def disaster_recovery():
    """
    模拟灾备恢复功能
    """
    data = request.json
    affected_servers = data.get("affected_servers", [])

    if not affected_servers:
        return jsonify({"success": False, "message": "No affected servers provided"}), 400

    try:
        # 模拟恢复数据和状态
        for server in affected_servers:
            if server in server_health:
                server_health[server]['status'] = "healthy"
                server_health[server]['load'] = random.uniform(10, 30)  # 恢复后随机负载

        log_operation(user_id=None, operation="disaster_recovery", status="success", details=f"Disaster recovery performed for: {affected_servers}")
        return jsonify({"success": True, "message": "Disaster recovery completed", "updated_health": server_health}), 200
    except Exception as e:
        log_operation(user_id=None, operation="disaster_recovery", status="failed", details=f"Error during disaster recovery: {str(e)}")
        return jsonify({"success": False, "message": f"Error during disaster recovery: {str(e)}"}), 500


# 故障检测并自动更新容器（服务器故障或容器故障）
@ha_bp.route('/api/ha/replace_container', methods=['POST'])
def replace_docker_container():
    """
    根据故障类型自动更新容器
    - 服务器故障：更新该服务器上的所有容器
    - 容器故障：更新单个容器并修改端口
    """
    data = request.json
    container_id = data.get("container_id")
    server_id = data.get("server_id")
    failure_type = data.get("failure_type", "container")  # 默认容器故障

    if not container_id or not server_id:
        return jsonify({"success": False, "message": "Missing container_id or server_id"}), 400

    try:
        if failure_type == "server":
            # 服务器故障，更新所有该服务器上的容器
            server = Server.query.get(server_id)
            if not server:
                return jsonify({"success": False, "message": "Server not found"}), 404

            containers = server.containers
            for container in containers:
                # 替换容器
                update_docker_container(container.id)
                # 更新 ACL 文件
                acl_config = update_acl_for_server(server)
                # 记录告警并通知
                alert = SystemAlert(
                    server_id=server_id,
                    alert_type="Server Failure",
                    message=f"All containers on server {server_id} are being replaced.",
                    timestamp=datetime.utcnow(),
                    status="active"
                )
                db.session.add(alert)
                db.session.commit()

                # 发送邮件通知管理员
                admins = User.query.filter_by(role="admin").all()
                for admin in admins:
                    send_notification_email(admin.email, "Server Failure Notification", f"All containers on server {server_id} have been replaced.")

            log_operation(user_id=None, operation="replace_docker_container", status="success", details=f"All containers on server {server_id} replaced.")
            return jsonify({"success": True, "message": f"All containers on server {server_id} replaced successfully"}), 200

        else:
            # 容器故障，更新单个容器并修改端口
            container_status = check_docker_health(container_id)
            if container_status != "running":
                # 替换容器并更新 ACL
                update_docker_container(container_id)
                # 更新 ACL 文件
                acl_config = update_acl_for_container(container_id)
                # 记录告警并通知
                alert = SystemAlert(
                    server_id=None,
                    alert_type="Docker Container Issue",
                    message=f"Docker container {container_id} is not running. Replacing container.",
                    timestamp=datetime.utcnow(),
                    status="active"
                )
                db.session.add(alert)
                db.session.commit()

                # 发送邮件通知管理员
                admins = User.query.filter_by(role="admin").all()
                for admin in admins:
                    send_notification_email(admin.email, "Docker Container Issue", f"Docker container {container_id} on server {server_id} is not running. It is being replaced.")

                log_operation(user_id=None, operation="replace_docker_container", status="success", details=f"Docker container {container_id} replaced.")
                return jsonify({"success": True, "message": f"Docker container {container_id} replaced successfully"}), 200

        return jsonify({"success": False, "message": "Invalid failure type"}), 400

    except Exception as e:
        log_operation(user_id=None, operation="replace_docker_container", status="failed", details=f"Error during container replacement: {str(e)}")
        return jsonify({"success": False, "message": f"Error during container replacement: {str(e)}"}), 500
