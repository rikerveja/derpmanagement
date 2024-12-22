from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import SystemAlert, User, Server, db
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
from app.utils.docker_utils import check_docker_health, get_docker_traffic
from app.utils.monitoring_utils import check_server_health
from flask_jwt_extended import jwt_required, get_jwt_identity

# 定义蓝图
alerts_bp = Blueprint('alerts', __name__)

# 实时告警
@alerts_bp.route('/api/alerts/realtime', methods=['GET'])
@jwt_required()  # 需要身份验证
def get_realtime_alerts():
    """
    获取实时系统告警
    """
    active_alerts = SystemAlert.query.filter_by(status="active").all()
    alert_data = [
        {
            "id": alert.id,
            "server_id": alert.server_id,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "status": alert.status
        }
        for alert in active_alerts
    ]

    if not alert_data:
        return jsonify({"success": True, "message": "No active alerts"}), 200

    return jsonify({"success": True, "alerts": alert_data}), 200


# 添加告警
@alerts_bp.route('/api/alerts/add', methods=['POST'])
@jwt_required()  # 需要身份验证
def add_alert():
    """
    添加新的系统告警
    """
    data = request.json
    server_id = data.get('server_id')
    alert_type = data.get('alert_type', 'General')
    message = data.get('message', 'No message provided')

    if not server_id:
        return jsonify({"success": False, "message": "Missing server_id"}), 400

    # 只允许管理员添加告警
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or user.role != "admin":
        log_operation(user_id=current_user, operation="add_alert", status="failed", details="Unauthorized access")
        return jsonify({"success": False, "message": "You are not authorized to perform this action"}), 403

    try:
        # 添加告警到数据库
        db_alert = SystemAlert(
            server_id=server_id,
            alert_type=alert_type,
            message=message,
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(db_alert)
        db.session.commit()

        # 发送邮件通知给管理员
        send_notification_email(user.email, "New Alert", f"A new alert has been added to server {server_id}.")

        log_operation(user_id=current_user, operation="add_alert", status="success", details=f"Alert added for server {server_id}")
        return jsonify({"success": True, "message": "Alert added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=current_user, operation="add_alert", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 增加月度流量不足告警
@alerts_bp.route('/api/alerts/traffic', methods=['POST'])
def check_monthly_traffic():
    """
    检查用户是否月度流量不足，并触发告警
    """
    data = request.json
    user_id = data.get('user_id')
    monthly_traffic_limit = data.get('monthly_traffic_limit')

    if not user_id or not monthly_traffic_limit:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    total_traffic = sum(container.upload_traffic + container.download_traffic for container in user.containers)
    if total_traffic > monthly_traffic_limit:
        # 触发流量告警
        alert = SystemAlert(
            server_id=None,
            alert_type="Monthly Traffic Limit Exceeded",
            message=f"Your total monthly traffic has exceeded the limit of {monthly_traffic_limit} MB.",
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(alert)
        db.session.commit()

        # 发送邮件通知
        send_notification_email(user.email, "Traffic Alert", f"Your total monthly traffic has exceeded the limit of {monthly_traffic_limit} MB.")
        log_operation(user_id=user.id, operation="check_monthly_traffic", status="success", details="Traffic alert triggered")
        return jsonify({"success": True, "message": "Monthly traffic alert triggered"}), 200

    return jsonify({"success": True, "message": "Traffic is within limits"}), 200


# 服务器健康状况告警
@alerts_bp.route('/api/alerts/server_health', methods=['POST'])
def check_server_health_status():
    """
    检查服务器健康状态并触发告警
    """
    data = request.json
    server_id = data.get('server_id')

    if not server_id:
        return jsonify({"success": False, "message": "Missing server_id"}), 400

    server = Server.query.get(server_id)
    if not server:
        return jsonify({"success": False, "message": "Server not found"}), 404

    health_status = check_server_health(server.ip)
    if not health_status['healthy']:
        # 触发服务器健康告警
        alert = SystemAlert(
            server_id=server.id,
            alert_type="Server Health Issue",
            message=f"Server {server.ip} is down or experiencing issues.",
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(alert)
        db.session.commit()

        # 发送邮件通知
        user = User.query.get(server.user_id)
        send_notification_email(user.email, "Server Health Alert", f"Server {server.ip} is down or experiencing issues.")
        log_operation(user_id=user.id, operation="check_server_health", status="success", details="Server health alert triggered")
        return jsonify({"success": True, "message": "Server health alert triggered"}), 200

    return jsonify({"success": True, "message": "Server is healthy"}), 200


# Docker 流量获取异常告警
@alerts_bp.route('/api/alerts/docker_traffic', methods=['POST'])
def check_docker_traffic_health():
    """
    检查 Docker 容器流量获取是否正常，并触发告警
    """
    data = request.json
    container_id = data.get('container_id')

    if not container_id:
        return jsonify({"success": False, "message": "Missing container_id"}), 400

    container = get_docker_traffic(container_id)
    if container is None or container['traffic_error']:
        # 触发 Docker 流量异常告警
        alert = SystemAlert(
            server_id=None,  # 这里不涉及特定服务器
            alert_type="Docker Traffic Issue",
            message=f"Docker container {container_id} traffic retrieval failed or data is abnormal.",
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(alert)
        db.session.commit()

        # 发送邮件通知
        user = User.query.get(container['user_id'])
        send_notification_email(user.email, "Docker Traffic Alert", f"Traffic retrieval for Docker container {container_id} failed.")
        log_operation(user_id=user.id, operation="check_docker_traffic_health", status="success", details="Docker traffic issue alert triggered")
        return jsonify({"success": True, "message": "Docker traffic issue alert triggered"}), 200

    return jsonify({"success": True, "message": "Docker traffic is normal"}), 200


# Docker 容器异常告警
@alerts_bp.route('/api/alerts/docker_container', methods=['POST'])
def check_docker_container_status():
    """
    检查 Docker 容器的状态并触发告警
    """
    data = request.json
    container_id = data.get('container_id')

    if not container_id:
        return jsonify({"success": False, "message": "Missing container_id"}), 400

    container_status = check_docker_health(container_id)
    if container_status != "running":
        # 触发容器异常告警
        alert = SystemAlert(
            server_id=None,  # 不涉及特定服务器
            alert_type="Docker Container Issue",
            message=f"Docker container {container_id} is not running.",
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(alert)
        db.session.commit()

        # 发送邮件通知
        user = User.query.get(container_status['user_id'])
        send_notification_email(user.email, "Docker Container Alert", f"Docker container {container_id} is not running.")
        log_operation(user_id=user.id, operation="check_docker_container_status", status="success", details="Docker container issue alert triggered")
        return jsonify({"success": True, "message": "Docker container issue alert triggered"}), 200

    return jsonify({"success": True, "message": "Docker container is running normally"}), 200


# 删除告警
@alerts_bp.route('/api/alerts/delete/<int:id>', methods=['DELETE'])
def delete_alert(id):
    """
    删除指定告警
    """
    alert = SystemAlert.query.get(id)
    if not alert:
        return jsonify({"success": False, "message": "Alert not found"}), 404

    try:
        db.session.delete(alert)
        db.session.commit()
        log_operation(user_id=None, operation="delete_alert", status="success", details=f"Alert {id} deleted successfully")
        return jsonify({"success": True, "message": "Alert deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=None, operation="delete_alert", status="failed", details=f"Error deleting alert: {str(e)}")
        return jsonify({"success": False, "message": f"Error deleting alert: {str(e)}"}), 500


# 查询所有告警
@alerts_bp.route('/api/alerts', methods=['GET'])
def get_all_alerts():
    """
    查询所有告警
    """
    alerts = SystemAlert.query.all()
    alert_data = [
        {
            "id": alert.id,
            "server_id": alert.server_id,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "status": alert.status
        }
        for alert in alerts
    ]

    return jsonify({"success": True, "alerts": alert_data}), 200
