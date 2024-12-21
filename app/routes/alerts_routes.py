from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import SystemAlert, db, User
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
from flask_jwt_extended import jwt_required, get_jwt_identity  # 用于身份验证

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

        log_operation(user_id=current_user, operation="add_alert", status="success", details=f"Alert added for server {server_id}")
        send_notification_email(user.email, "New Alert", f"A new alert has been added to server {server_id}.")
        return jsonify({"success": True, "message": "Alert added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=current_user, operation="add_alert", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 获取历史告警记录
@alerts_bp.route('/api/alerts/history', methods=['GET'])
@jwt_required()  # 需要身份验证
def get_alert_history():
    """
    查询历史告警记录
    支持按服务器 ID、告警类型和状态过滤
    """
    server_id = request.args.get('server_id')
    alert_type = request.args.get('alert_type')
    status = request.args.get('status')  # 筛选告警状态（如 active, cleared, resolved）
    start_date = request.args.get('start_date')  # 起始时间（可选）
    end_date = request.args.get('end_date')  # 结束时间（可选）

    query = SystemAlert.query
    if server_id:
        query = query.filter_by(server_id=server_id)
    if alert_type:
        query = query.filter_by(alert_type=alert_type)
    if status:
        query = query.filter_by(status=status)
    if start_date:
        query = query.filter(SystemAlert.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(SystemAlert.timestamp <= datetime.strptime(end_date, '%Y-%m-%d'))

    alerts = query.all()
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


# 清除告警
@alerts_bp.route('/api/alerts/clear', methods=['POST'])
@jwt_required()  # 需要身份验证
def clear_alerts():
    """
    清除实时告警或特定服务器的告警
    """
    data = request.json
    server_id = data.get('server_id')

    # 只允许管理员清除告警
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or user.role != "admin":
        log_operation(user_id=current_user, operation="clear_alerts", status="failed", details="Unauthorized access")
        return jsonify({"success": False, "message": "You are not authorized to perform this action"}), 403

    try:
        query = SystemAlert.query.filter_by(status="active")
        if server_id:
            query = query.filter_by(server_id=server_id)

        # 标记告警为已清除
        alerts = query.all()
        for alert in alerts:
            alert.status = "cleared"

        db.session.commit()
        log_operation(user_id=current_user, operation="clear_alerts", status="success", details=f"Cleared alerts for server: {server_id or 'all'}")
        return jsonify({"success": True, "message": "Alerts cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=current_user, operation="clear_alerts", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 手动触发告警
@alerts_bp.route('/api/alerts/manual_trigger', methods=['POST'])
@jwt_required()  # 需要身份验证
def manual_trigger_alert():
    """
    手动触发系统告警
    """
    data = request.json
    server_id = data.get('server_id')
    message = data.get('message', 'Manual alert triggered')

    if not server_id:
        return jsonify({"success": False, "message": "Missing server_id"}), 400

    # 只允许管理员触发告警
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or user.role != "admin":
        log_operation(user_id=current_user, operation="manual_trigger_alert", status="failed", details="Unauthorized access")
        return jsonify({"success": False, "message": "You are not authorized to perform this action"}), 403

    try:
        # 添加到数据库
        db_alert = SystemAlert(
            server_id=server_id,
            alert_type="Manual",
            message=message,
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(db_alert)
        db.session.commit()

        log_operation(user_id=current_user, operation="manual_trigger_alert", status="success", details=f"Manual alert triggered for server {server_id}")
        return jsonify({"success": True, "message": "Manual alert triggered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=current_user, operation="manual_trigger_alert", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
