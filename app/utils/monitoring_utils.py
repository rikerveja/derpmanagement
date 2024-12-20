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
                resolved=False,
                server_id=log.server_id  # 确保告警与服务器相关联
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
