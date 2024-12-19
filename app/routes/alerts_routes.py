from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import SystemAlert, db
from app.utils.logging_utils import log_operation

# 定义蓝图
alerts_bp = Blueprint('alerts', __name__)

# 模拟当前告警状态存储
current_alerts = []


# 实时告警
@alerts_bp.route('/api/alerts/realtime', methods=['GET'])
def get_realtime_alerts():
    """
    获取实时系统告警
    """
    if not current_alerts:
        return jsonify({"success": True, "message": "No active alerts"}), 200

    return jsonify({"success": True, "alerts": current_alerts}), 200


# 添加告警
@alerts_bp.route('/api/alerts/add', methods=['POST'])
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

    alert = {
        "server_id": server_id,
        "alert_type": alert_type,
        "message": message,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    current_alerts.append(alert)

    # 记录告警到数据库
    db_alert = SystemAlert(
        server_id=server_id,
        alert_type=alert_type,
        message=message,
        timestamp=datetime.utcnow()
    )
    db.session.add(db_alert)
    try:
        db.session.commit()
        log_operation(user_id=None, operation="add_alert", status="success", details=f"Alert added: {alert}")
        return jsonify({"success": True, "message": "Alert added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=None, operation="add_alert", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 获取历史告警记录
@alerts_bp.route('/api/alerts/history', methods=['GET'])
def get_alert_history():
    """
    查询历史告警记录
    支持按服务器 ID 和告警类型过滤
    """
    server_id = request.args.get('server_id')
    alert_type = request.args.get('alert_type')

    query = SystemAlert.query
    if server_id:
        query = query.filter_by(server_id=server_id)
    if alert_type:
        query = query.filter_by(alert_type=alert_type)

    alerts = query.all()
    alert_data = [
        {
            "id": alert.id,
            "server_id": alert.server_id,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "timestamp": alert.timestamp
        }
        for alert in alerts
    ]

    return jsonify({"success": True, "alerts": alert_data}), 200


# 清除告警
@alerts_bp.route('/api/alerts/clear', methods=['POST'])
def clear_alerts():
    """
    清除实时告警
    """
    data = request.json
    server_id = data.get('server_id')

    if server_id:
        global current_alerts
        current_alerts = [alert for alert in current_alerts if alert['server_id'] != server_id]
        db_alerts = SystemAlert.query.filter_by(server_id=server_id).all()

        # 从数据库中删除
        for alert in db_alerts:
            db.session.delete(alert)
    else:
        # 清除所有告警
        current_alerts = []
        db_alerts = SystemAlert.query.all()
        for alert in db_alerts:
            db.session.delete(alert)

    try:
        db.session.commit()
        log_operation(user_id=None, operation="clear_alerts", status="success", details=f"Cleared alerts for server: {server_id or 'all'}")
        return jsonify({"success": True, "message": "Alerts cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=None, operation="clear_alerts", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 手动触发告警
@alerts_bp.route('/api/alerts/manual_trigger', methods=['POST'])
def manual_trigger_alert():
    """
    手动触发系统告警
    """
    data = request.json
    server_id = data.get('server_id')
    message = data.get('message', 'Manual alert triggered')

    if not server_id:
        return jsonify({"success": False, "message": "Missing server_id"}), 400

    alert = {
        "server_id": server_id,
        "alert_type": "Manual",
        "message": message,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    current_alerts.append(alert)

    # 添加到数据库
    db_alert = SystemAlert(
        server_id=server_id,
        alert_type="Manual",
        message=message,
        timestamp=datetime.utcnow()
    )
    db.session.add(db_alert)
    try:
        db.session.commit()
        log_operation(user_id=None, operation="manual_trigger_alert", status="success", details=f"Manual alert triggered: {alert}")
        return jsonify({"success": True, "message": "Manual alert triggered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=None, operation="manual_trigger_alert", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
