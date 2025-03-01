from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import SystemAlert, User, Server, db, AlarmRule
from app import db
from app.utils.logging_utils import log_operation
from app.utils.notifications_utils import send_notification_email
from app.utils.docker_utils import check_docker_health, get_docker_traffic
from app.utils.monitoring_utils import check_server_health
from flask_jwt_extended import jwt_required, get_jwt_identity
import redis
import json
import os

# 定义蓝图
alerts_bp = Blueprint('alerts', __name__, url_prefix='/api')

# 实时告警
@alerts_bp.route('/alerts/realtime', methods=['GET'])
@jwt_required()  # 需要身份验证
def get_realtime_alerts():
    """
    获取实时系统告警，并包含服务器信息
    """
    active_alerts = SystemAlert.query.filter_by(status="active").all()
    alert_data = []
    
    for alert in active_alerts:
        alert_info = {
            "id": alert.id,
            "server_id": alert.server_id,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "status": alert.status,
            "server_info": None
        }
        
        if alert.server_id:
            server = Server.query.get(alert.server_id)
            if server:
                alert_info["server_info"] = {
                    "id": server.id,
                    "name": server.server_name,
                    "ip": server.ip_address,
                    "region": server.region
                }
        
        alert_data.append(alert_info)

    if not alert_data:
        return jsonify({"success": True, "message": "No active alerts"}), 200

    return jsonify({"success": True, "alerts": alert_data}), 200


# 添加告警
@alerts_bp.route('/alerts/add', methods=['POST'])
@jwt_required()
def add_alert():
    """
    添加新的系统告警
    """
    data = request.json
    server_id = data.get('server_id')
    alert_type = data.get('alert_type', 'server')
    message = data.get('message', 'No message provided')
    severity = data.get('severity', 'medium')  # 新增：优先级
    details = data.get('details', {})  # 新增：详细信息

    if not server_id:
        return jsonify({"success": False, "message": "Missing server_id"}), 400

    if severity not in ['low', 'medium', 'high', 'critical']:
        return jsonify({"success": False, "message": "Invalid severity level"}), 400

    # 只允许管理员添加告警
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or user.role != "admin":
        log_operation(user_id=current_user, operation="add_alert", status="failed", details="Unauthorized access")
        return jsonify({"success": False, "message": "You are not authorized to perform this action"}), 403

    try:
        # 添加告警到数据库
        db_alert = SystemAlert(
            target_id=server_id,
            target_type='server',
            alert_type=alert_type,
            message=message,
            severity=severity,  # 设置优先级
            details=details,    # 存储详细信息
            status="active",
            created_at=datetime.utcnow()
        )
        db.session.add(db_alert)
        db.session.commit()

        # 发送邮件通知给管理员
        send_notification_email(
            user.email, 
            f"{severity.upper()} Alert", 
            f"A new {severity} priority alert has been added for server {server_id}."
        )

        log_operation(
            user_id=current_user, 
            operation="add_alert", 
            status="success", 
            details=f"Alert added for server {server_id} with {severity} priority"
        )
        
        return jsonify({
            "success": True, 
            "message": "Alert added successfully",
            "alert": {
                "id": db_alert.id,
                "server_id": db_alert.target_id,
                "alert_type": db_alert.alert_type,
                "message": db_alert.message,
                "severity": db_alert.severity,
                "status": db_alert.status,
                "created_at": db_alert.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=current_user, operation="add_alert", status="failed", details=f"Error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 增加月度流量不足告警
@alerts_bp.route('/alerts/traffic', methods=['POST'])
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
@alerts_bp.route('/alerts/server_health', methods=['POST'])
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
@alerts_bp.route('/alerts/docker_traffic', methods=['POST'])
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
@alerts_bp.route('/alerts/docker_container', methods=['POST'])
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
@alerts_bp.route('/alerts/<int:id>', methods=['DELETE'])
def delete_alert(id):
    """
    删除指定告警
    """
    alert = SystemAlert.query.get_or_404(id)
    if not alert:
        return jsonify({"success": False, "message": "Alert not found"}), 404

    try:
        db.session.delete(alert)
        db.session.commit()
        log_operation(user_id=None, operation="delete_alert", details=f"Alert {id} deleted successfully")
        return jsonify({"success": True, "message": "Alert deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        log_operation(user_id=None, operation="delete_alert", details=f"Error deleting alert: {str(e)}")
        return jsonify({"success": False, "message": f"Error deleting alert: {str(e)}"}), 500


# 查询所有告警
@alerts_bp.route('/alerts', methods=['GET'])
def get_all_alerts():
    """
    查询所有告警，包含完整信息
    """
    alerts = SystemAlert.query.all()
    alert_data = []
    
    for alert in alerts:
        alert_info = {
            "id": alert.id,
            "server_id": alert.target_id if alert.target_type == 'server' else None,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "severity": alert.severity,
            "status": alert.status,
            "created_at": alert.created_at.isoformat(),
            "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "resolved_by": alert.resolved_by,
            "details": alert.details or {},
            "server_info": None
        }
        
        if alert.target_type == 'server' and alert.target_id:
            server = Server.query.get(alert.target_id)
            if server:
                alert_info["server_info"] = {
                    "id": server.id,
                    "name": server.server_name,
                    "ip": server.ip_address,
                    "region": server.region
                }
        
        alert_data.append(alert_info)

    return jsonify({"success": True, "alerts": alert_data}), 200


@alerts_bp.route('/alerts/settings', methods=['GET'])
def get_alert_settings():
    """获取告警设置"""
    try:
        print("Fetching alert settings...")
        
        # 1. 首先尝试从 Redis 获取设置
        redis_client = redis.StrictRedis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=6379,
            db=0
        )
        settings_json = redis_client.get('alert_settings')
        
        if settings_json:
            print("Found settings in Redis")
            return jsonify({
                "success": True,
                "settings": json.loads(settings_json)
            })
        
        # 2. 从数据库获取
        print("Fetching settings from database...")
        rules = AlarmRule.query.filter_by(category='global').all()
        print(f"Found {len(rules)} rules in database")
        
        settings = {
            'serverHealthCheck': True,
            'dockerHealthCheck': True,
            'trafficAlert': True,
            'emailNotification': True,
            'checkInterval': 5,
            'thresholds': {
                'traffic': 90,
                'cpu': 80,
                'memory': 80,
                'disk': 85
            }
        }
        
        # 从规则中更新设置
        for rule in rules:
            print(f"Processing rule: {rule.name}, threshold: {rule.threshold}, condition: {rule.alert_condition}")
            if rule.alert_condition == 'cpu_usage':
                settings['thresholds']['cpu'] = float(rule.threshold)
            elif rule.alert_condition == 'memory_usage':
                settings['thresholds']['memory'] = float(rule.threshold)
            elif rule.alert_condition == 'disk_usage':
                settings['thresholds']['disk'] = float(rule.threshold)
            elif rule.alert_condition == 'traffic_usage':
                settings['thresholds']['traffic'] = float(rule.threshold)
            elif rule.alert_condition == 'check_interval':
                settings['checkInterval'] = float(rule.threshold)
            elif rule.alert_condition == 'server_health':
                settings['serverHealthCheck'] = rule.threshold > 0
            elif rule.alert_condition == 'docker_health':
                settings['dockerHealthCheck'] = rule.threshold > 0
            elif rule.alert_condition == 'traffic_monitor':
                settings['trafficAlert'] = rule.threshold > 0
            elif rule.alert_condition == 'email_notify':
                settings['emailNotification'] = rule.threshold > 0
        
        # 将数据同步到 Redis
        print("Syncing settings to Redis...")
        redis_client.set('alert_settings', json.dumps(settings))
        
        return jsonify({
            "success": True,
            "settings": settings
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Error getting settings: {error_msg}")
        return jsonify({"success": False, "message": error_msg}), 500

@alerts_bp.route('/alerts/settings', methods=['POST'])
def update_alert_settings():
    """更新告警设置"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "message": "未接收到设置数据"
            }), 400

        print("Received settings data:", data)
        
        # 验证数据格式
        required_fields = ['serverHealthCheck', 'dockerHealthCheck', 'trafficAlert', 
                          'emailNotification', 'checkInterval', 'thresholds']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "设置数据格式不正确"
            }), 400
        
        now = datetime.utcnow()
        
        try:
            # 先删除所有全局设置
            print("Deleting existing global rules...")
            AlarmRule.query.filter_by(category='global').delete()
            db.session.commit()
            print("Existing global rules deleted successfully")
        except Exception as e:
            print(f"Error deleting existing rules: {str(e)}")
            db.session.rollback()
            raise
        
        # 创建新的规则
        new_rules = []
        
        # 首先添加开关规则（优先处理）
        switches = [
            {
                'name': '服务器健康检查',
                'alert_condition': 'server_health_check',
                'is_active': data['serverHealthCheck'],
                'description': '检测服务器运行状态'
            },
            {
                'name': 'Docker容器检查',
                'alert_condition': 'docker_health_check',
                'is_active': data['dockerHealthCheck'],
                'description': '监控容器运行状态'
            },
            {
                'name': '流量告警开关',
                'alert_condition': 'traffic_alert_switch',
                'is_active': data['trafficAlert'],
                'description': '监控用户流量使用情况'
            },
            {
                'name': '邮件通知开关',
                'alert_condition': 'email_notification_switch',
                'is_active': data['emailNotification'],
                'description': '发送告警邮件通知'
            }
        ]
        
        print("\nCreating switch rules...")
        for switch in switches:
            try:
                print(f"Creating switch rule: {switch['name']}, state: {switch['is_active']}")
                rule = AlarmRule(
                    name=switch['name'],
                    category='global',
                    alert_condition=switch['alert_condition'],
                    threshold=1.0 if switch['is_active'] else 0.0,
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                    severity='medium',
                    description=switch['description'],
                    created_by=1
                )
                new_rules.append(rule)
                print(f"Switch rule created: {rule.name}")
            except Exception as e:
                print(f"Error creating switch rule {switch['name']}: {str(e)}")
                raise
        
        # 然后添加阈值规则
        thresholds = [
            {
                'name': 'CPU使用率告警',
                'alert_condition': 'cpu_usage',
                'threshold': float(data['thresholds']['cpu']),
                'description': 'CPU使用率超过阈值'
            },
            {
                'name': '内存使用率告警',
                'alert_condition': 'memory_usage',
                'threshold': float(data['thresholds']['memory']),
                'description': '内存使用率超过阈值'
            },
            {
                'name': '磁盘使用率告警',
                'alert_condition': 'disk_usage',
                'threshold': float(data['thresholds']['disk']),
                'description': '磁盘使用率超过阈值'
            },
            {
                'name': '流量使用率告警',
                'alert_condition': 'traffic_usage',
                'threshold': float(data['thresholds']['traffic']),
                'description': '流量使用率超过阈值'
            },
            {
                'name': '检查间隔设置',
                'alert_condition': 'check_interval',
                'threshold': float(data['checkInterval']),
                'description': '告警检查时间间隔（分钟）'
            }
        ]
        
        print("\nCreating threshold rules...")
        for threshold in thresholds:
            try:
                print(f"Creating threshold rule: {threshold['name']}, value: {threshold['threshold']}")
                rule = AlarmRule(
                    name=threshold['name'],
                    category='global',
                    alert_condition=threshold['alert_condition'],
                    threshold=threshold['threshold'],
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                    severity='medium',
                    description=threshold['description'],
                    created_by=1
                )
                new_rules.append(rule)
                print(f"Threshold rule created: {rule.name}")
            except Exception as e:
                print(f"Error creating threshold rule {threshold['name']}: {str(e)}")
                raise
        
        try:
            print(f"\nSaving {len(new_rules)} rules to database...")
            for rule in new_rules:
                print(f"Saving rule: {rule.name}, condition: {rule.alert_condition}, threshold: {rule.threshold}")
                db.session.add(rule)
            
            print("Committing changes...")
            db.session.commit()
            print("All rules saved successfully")
        except Exception as e:
            print(f"Error saving rules to database: {str(e)}")
            db.session.rollback()
            raise
        
        # 验证数据是否保存成功
        saved_rules = AlarmRule.query.filter_by(category='global').all()
        print(f"\nVerification: Found {len(saved_rules)} rules in database")
        for rule in saved_rules:
            print(f"Saved rule: {rule.name}, condition: {rule.alert_condition}, threshold: {rule.threshold}")
        
        # 同步到 Redis
        try:
            print("\nSyncing to Redis...")
            redis_client = redis.StrictRedis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=6379,
                db=0
            )
            
            settings = {
                'serverHealthCheck': data['serverHealthCheck'],
                'dockerHealthCheck': data['dockerHealthCheck'],
                'trafficAlert': data['trafficAlert'],
                'emailNotification': data['emailNotification'],
                'checkInterval': data['checkInterval'],
                'thresholds': data['thresholds']
            }
            redis_client.set('alert_settings', json.dumps(settings))
            print("Redis sync completed")
        except Exception as e:
            print(f"Error syncing to Redis: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": "设置已更新",
            "saved_rules_count": len(saved_rules)
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Error updating settings: {error_msg}")
        return jsonify({
            "success": False,
            "message": f"保存设置失败：{error_msg}"
        }), 500

@alerts_bp.route('/alerts/rules', methods=['GET'])
def get_rules():
    # 支持按类别过滤
    category = request.args.get('category')
    query = AlarmRule.query
    
    if category:
        query = query.filter(AlarmRule.category == category)
    
    rules = query.all()
    return jsonify({"success": True, "data": [rule.to_dict() for rule in rules]})

@alerts_bp.route('/alerts/rules', methods=['POST'])
def create_rule():
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['name', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

    try:
        # 创建新的告警规则
        rule = AlarmRule(
            name=data['name'],
            alert_condition=data.get('alert_condition'),
            threshold=data.get('threshold'),
            is_active=data.get('is_active', True),
            category=data['category'],
            check_type=data.get('check_type'),
            check_interval=data.get('check_interval', 300),
            notification_methods=data.get('notification_methods', {}),
            description=data.get('description')
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({"success": True, "data": rule.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@alerts_bp.route('/alerts/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    rule = AlarmRule.query.get_or_404(rule_id)
    data = request.get_json()
    
    try:
        # 更新规则字段
        if 'name' in data:
            rule.name = data['name']
        if 'alert_condition' in data:
            rule.alert_condition = data['alert_condition']
        if 'threshold' in data:
            rule.threshold = data['threshold']
        if 'is_active' in data:
            rule.is_active = data['is_active']
        if 'category' in data:
            rule.category = data['category']
        if 'check_type' in data:
            rule.check_type = data['check_type']
        if 'check_interval' in data:
            rule.check_interval = data['check_interval']
        if 'notification_methods' in data:
            rule.notification_methods = data['notification_methods']
        if 'description' in data:
            rule.description = data['description']
            
        db.session.commit()
        return jsonify({"success": True, "data": rule.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@alerts_bp.route('/alerts/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    rule = AlarmRule.query.get_or_404(rule_id)
    try:
        db.session.delete(rule)
        db.session.commit()
        return jsonify({"success": True, "message": "Rule deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# 更新告警状态
@alerts_bp.route('/alerts/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_alert_status(id):
    """
    更新告警状态和解决信息
    """
    data = request.json
    new_status = data.get('status')
    resolution_note = data.get('resolution_note', '')
    
    if not new_status:
        return jsonify({"success": False, "message": "Missing status parameter"}), 400
        
    if new_status not in ['active', 'acknowledged', 'resolved']:
        return jsonify({"success": False, "message": "Invalid status value"}), 400
    
    try:
        alert = SystemAlert.query.get_or_404(id)
        alert.status = new_status
        
        # 更新详细信息
        details = alert.details or {}
        if resolution_note:
            details['resolution_note'] = resolution_note
        alert.details = details
        
        # 如果状态是已解决，更新解决时间和解决人
        current_user = get_jwt_identity()
        if new_status == 'resolved':
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = current_user
        
        db.session.commit()
        
        # 记录操作日志
        log_operation(
            user_id=current_user,
            operation="update_alert_status",
            status="success",
            details=f"Alert {id} status updated to {new_status}"
        )
        
        return jsonify({
            "success": True,
            "message": "Alert status updated successfully",
            "alert": {
                "id": alert.id,
                "status": alert.status,
                "resolution_note": details.get('resolution_note', ''),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "resolved_by": alert.resolved_by
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# 更新告警优先级
@alerts_bp.route('/alerts/<int:id>/severity', methods=['PUT'])
@jwt_required()
def update_alert_severity(id):
    """
    更新告警优先级
    """
    data = request.json
    new_severity = data.get('severity')
    reason = data.get('reason', '')
    
    if not new_severity:
        return jsonify({"success": False, "message": "Missing severity parameter"}), 400
        
    if new_severity not in ['low', 'medium', 'high', 'critical']:
        return jsonify({"success": False, "message": "Invalid severity value"}), 400
    
    try:
        alert = SystemAlert.query.get_or_404(id)
        old_severity = alert.severity
        alert.severity = new_severity
        
        # 记录优先级变更原因
        details = alert.details or {}
        details['severity_changes'] = details.get('severity_changes', [])
        details['severity_changes'].append({
            'from': old_severity,
            'to': new_severity,
            'reason': reason,
            'changed_at': datetime.utcnow().isoformat(),
            'changed_by': get_jwt_identity()
        })
        alert.details = details
        
        db.session.commit()
        
        # 记录操作日志
        current_user = get_jwt_identity()
        log_operation(
            user_id=current_user,
            operation="update_alert_severity",
            status="success",
            details=f"Alert {id} severity updated from {old_severity} to {new_severity}"
        )
        
        return jsonify({
            "success": True,
            "message": "Alert severity updated successfully",
            "alert": {
                "id": alert.id,
                "severity": alert.severity,
                "severity_history": details.get('severity_changes', [])
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
