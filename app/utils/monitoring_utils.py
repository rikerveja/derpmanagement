from app.models import MonitoringLog, Server, SystemAlert
from app import db
from datetime import datetime, timedelta
import random
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def log_metric(metric_name, value, server_id=None):
    """
    记录监控指标到数据库
    :param metric_name: 指标名称
    :param value: 指标值
    :param server_id: 关联的服务器 ID（可选）
    """
    try:
        monitoring_log = MonitoringLog(
            metric=metric_name,
            value=value,
            server_id=server_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(monitoring_log)
        db.session.commit()
        logging.info(f"Logged metric: {metric_name} with value: {value} for server_id: {server_id}")
    except Exception as e:
        logging.error(f"Failed to log metric: {e}")
        db.session.rollback()


def get_recent_metrics(metric_name, duration_minutes=60):
    """
    获取最近指定时间范围内的监控指标
    :param metric_name: 指标名称
    :param duration_minutes: 时间范围，单位为分钟
    :return: 最近的监控指标列表
    """
    try:
        time_threshold = datetime.utcnow() - timedelta(minutes=duration_minutes)
        metrics = MonitoringLog.query.filter(
            MonitoringLog.metric == metric_name,
            MonitoringLog.timestamp >= time_threshold
        ).order_by(MonitoringLog.timestamp.desc()).all()
        return metrics
    except Exception as e:
        logging.error(f"Failed to fetch metrics: {e}")
        return []


def check_server_health():
    """
    检查服务器健康状态并记录到数据库，同时生成告警（如需）
    :return: 不健康的服务器列表
    """
    unhealthy_servers = []
    try:
        servers = Server.query.all()
        for server in servers:
            # 模拟健康检查逻辑（可替换为真实逻辑）
            health_status = random.choice(["healthy", "unhealthy"])
            if health_status == "unhealthy":
                unhealthy_servers.append(server)
                log_metric("server_health", 0, server_id=server.id)
                server.status = "unhealthy"

                # 创建健康告警
                create_alert(
                    server_id=server.id,
                    alert_type="Health",
                    description=f"Server {server.id} is unhealthy in region {server.region}"
                )
            else:
                log_metric("server_health", 1, server_id=server.id)
                server.status = "healthy"

        db.session.commit()
        logging.info(f"Health check completed. Unhealthy servers: {[server.id for server in unhealthy_servers]}")
    except Exception as e:
        logging.error(f"Failed to check server health: {e}")
        db.session.rollback()

    return unhealthy_servers


def send_health_alert(unhealthy_servers):
    """
    发送服务器不健康告警日志
    :param unhealthy_servers: 不健康的服务器列表
    """
    for server in unhealthy_servers:
        logging.warning(f"Alert: Server {server.id} is unhealthy in region {server.region}.")


def perform_load_balancing(threshold=70):
    """
    执行负载均衡逻辑
    :param threshold: 负载阈值（超过该值的服务器需要平衡）
    """
    try:
        servers = Server.query.all()
        for server in servers:
            # 模拟负载值（可替换为真实逻辑）
            current_load = random.uniform(0, 100)
            log_metric("server_load", current_load, server_id=server.id)
            if current_load > threshold:
                # 模拟负载均衡逻辑
                logging.info(f"Server {server.id} is over threshold ({current_load}%). Balancing load...")
                server.load = random.uniform(20, 50)  # 降低负载
        db.session.commit()
        logging.info("Load balancing completed.")
    except Exception as e:
        logging.error(f"Failed to perform load balancing: {e}")
        db.session.rollback()


def create_alert(server_id, alert_type, description):
    """
    创建系统告警记录
    :param server_id: 服务器 ID
    :param alert_type: 告警类型（如健康检查、负载高）
    :param description: 告警描述
    """
    try:
        alert = SystemAlert(
            server_id=server_id,
            alert_type=alert_type,
            message=description,
            timestamp=datetime.utcnow(),
            status="active"
        )
        db.session.add(alert)
        db.session.commit()
        logging.info(f"Alert created: {description}")
    except Exception as e:
        logging.error(f"Failed to create alert: {e}")
        db.session.rollback()


def resolve_alert(alert_id):
    """
    标记告警为已解决
    :param alert_id: 告警 ID
    """
    try:
        alert = SystemAlert.query.get(alert_id)
        if not alert:
            logging.warning(f"Alert with ID {alert_id} not found.")
            return

        alert.status = "resolved"
        db.session.commit()
        logging.info(f"Alert {alert_id} resolved.")
    except Exception as e:
        logging.error(f"Failed to resolve alert: {e}")
        db.session.rollback()


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
                server_id=log.server_id,
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
