from flask import Blueprint, jsonify, request
import random
from app.utils.logging_utils import log_operation
# 循环导入，删除from app.utils.monitoring_utils import generate_alerts, analyze_server_load

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
def check_server_health():
    """
    查看所有服务器健康状态
    """
    return jsonify({"success": True, "server_health": server_health}), 200


# 单个服务器健康检查
@ha_bp.route('/api/ha/health/<server_id>', methods=['GET'])
def check_individual_server_health(server_id):
    """
    查看单个服务器健康状态
    """
    server_info = server_health.get(server_id)
    if not server_info:
        return jsonify({"success": False, "message": "Server not found"}), 404

    # 模拟实时检查健康状态（可以改为真实健康检查逻辑）
    server_info['status'] = "healthy" if random.random() > 0.2 else "unhealthy"
    return jsonify({"success": True, "server_id": server_id, "status": server_info['status']}), 200


# 故障切换
@ha_bp.route('/api/ha/failover', methods=['POST'])
def failover():
    """
    故障切换服务到备用服务器
    """
    unhealthy_servers = [key for key, data in server_health.items() if data['status'] == "unhealthy"]
    if not unhealthy_servers:
        log_operation(user_id=None, operation="failover", status="success", details="No unhealthy servers detected")
        return jsonify({"success": False, "message": "No unhealthy servers detected"}), 200

    # 模拟切换到备用服务器
    for server in unhealthy_servers:
        server_health[server]['status'] = "switched"
        server_health[server]['load'] = 0  # 清空负载

    log_operation(user_id=None, operation="failover", status="success", details=f"Failover completed for: {unhealthy_servers}")
    return jsonify({"success": True, "message": "Failover completed", "updated_health": server_health}), 200


# 负载均衡
@ha_bp.route('/api/ha/load_balance', methods=['POST'])
def load_balance():
    """
    根据服务器负载执行流量重新分配
    """
    threshold = request.json.get("threshold", 70)  # 默认负载均衡阈值为 70%
    high_load_servers = [key for key, data in server_health.items() if data['load'] > threshold]

    if not high_load_servers:
        return jsonify({"success": True, "message": "No servers exceed the load threshold"}), 200

    # 模拟重新分配流量
    for server in high_load_servers:
        server_health[server]['load'] = random.uniform(20, 50)  # 降低高负载服务器的负载

    log_operation(user_id=None, operation="load_balance", status="success", details=f"Load balanced for: {high_load_servers}")
    return jsonify({"success": True, "message": "Load balancing completed", "updated_health": server_health}), 200


# 灾备恢复
@ha_bp.route('/api/ha/disaster_recovery', methods=['POST'])
def disaster_recovery():
    """
    模拟灾备恢复功能
    """
    affected_servers = request.json.get("affected_servers", [])
    if not affected_servers:
        return jsonify({"success": False, "message": "No affected servers provided"}), 400

    # 模拟恢复数据和状态
    for server in affected_servers:
        if server in server_health:
            server_health[server]['status'] = "healthy"
            server_health[server]['load'] = random.uniform(10, 30)  # 恢复后随机负载

    log_operation(user_id=None, operation="disaster_recovery", status="success", details=f"Disaster recovery performed for: {affected_servers}")
    return jsonify({"success": True, "message": "Disaster recovery completed", "updated_health": server_health}), 200


# 负载分析
@ha_bp.route('/api/ha/load_analysis', methods=['GET'])
def load_analysis():
    """
    返回服务器负载分析结果
    """
    results = analyze_server_load()
    return jsonify({"success": True, "load_analysis": results}), 200


# 生成系统告警
@ha_bp.route('/api/ha/generate_alerts', methods=['POST'])
def alerts():
    """
    生成告警
    """
    try:
        generate_alerts()
        return jsonify({"success": True, "message": "Alerts generated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

import logging
from app.models import MonitoringLog, Server, SystemAlert
from sqlalchemy import func
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

def analyze_server_load():
    """
    分析服务器负载
    返回一个服务器负载统计的列表
    """
    servers = Server.query.all()
    load_results = []

    for server in servers:
        avg_load = (
            MonitoringLog.query.filter_by(server_id=server.id)
            .with_entities(func.avg(MonitoringLog.value).label('avg_load'))
            .scalar()
        )
        load_results.append({
            "server_id": server.id,
            "ip": server.ip,
            "region": server.region,
            "average_load": avg_load
        })
        logging.info(f"Analyzed load for server {server.ip}: {avg_load}")

    return load_results

def generate_alerts():
    """
    生成系统告警（如服务器过载）
    """
    threshold = 80.0  # 负载阈值
    now = datetime.utcnow()
    recent_logs = MonitoringLog.query.filter(
        MonitoringLog.timestamp >= now - timedelta(minutes=10)
    ).all()

    for log in recent_logs:
        if log.value > threshold:
            # 检查是否已有未解决的告警
            existing_alert = SystemAlert.query.filter_by(
                alert_type="High Load",
                resolved=False
            ).first()

            if not existing_alert:
                # 创建新的告警
                alert = SystemAlert(
                    alert_type="High Load",
                    severity="critical",
                    message=f"Server {log.server.ip} is overloaded with a load of {log.value}",
                    timestamp=now,
                    resolved=False
                )
                db.session.add(alert)
                logging.warning(f"Generated alert for server {log.server.ip} with load {log.value}")

    db.session.commit()
    logging.info("Alerts generation completed.")
