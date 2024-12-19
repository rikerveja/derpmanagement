from app.models import MonitoringLog, Server
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
    检查服务器健康状态
    :return: 不健康的服务器列表
    """
    unhealthy_servers = []
    try:
        servers = Server.query.all()
        for server in servers:
            # 模拟健康检查（可替换为真实逻辑）
            health_status = random.choice(["healthy", "unhealthy"])
            if health_status == "unhealthy":
                unhealthy_servers.append(server)
                log_metric("server_health", 0, server_id=server.id)
                server.status = "unhealthy"
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
    发送服务器不健康告警
    :param unhealthy_servers: 不健康的服务器列表
    """
    for server in unhealthy_servers:
        logging.warning(f"Alert: Server {server.id} is unhealthy in region {server.region}.")

def perform_load_balancing(threshold=70):
    """
    执行负载均衡
    :param threshold: 负载阈值（超过该值的服务器需要平衡）
    """
    try:
        servers = Server.query.all()
        for server in servers:
            # 模拟当前负载值（可替换为真实逻辑）
            current_load = random.uniform(0, 100)
            log_metric("server_load", current_load, server_id=server.id)
            if current_load > threshold:
                # 模拟负载均衡逻辑（可扩展为真实分流逻辑）
                logging.info(f"Server {server.id} is over threshold. Balancing load...")
                server.load = random.uniform(20, 50)  # 降低负载
        db.session.commit()
        logging.info("Load balancing completed.")
    except Exception as e:
        logging.error(f"Failed to perform load balancing: {e}")
        db.session.rollback()
