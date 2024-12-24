import logging
import paramiko
from app.models import MonitoringLog, Server, SystemAlert, db
from sqlalchemy import func
from datetime import datetime, timedelta
from app.config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('monitoring_utils')

# 动态获取负载阈值
THRESHOLD = Config.HIGH_LOAD_THRESHOLD or 80.0


def check_server_health(ssh_host, ssh_user, ssh_password):
    """
    检查远程服务器的健康状态。
    :param ssh_host: 远程主机地址
    :param ssh_user: SSH 用户名
    :param ssh_password: SSH 密码
    :return: 服务器健康状态的字典
    """
    try:
        # 创建 SSH 连接
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_host, username=ssh_user, password=ssh_password)
        logger.info("SSH connection established for server health check.")

        # 检查 CPU 使用率
        stdin, stdout, stderr = client.exec_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        cpu_usage = stdout.read().decode('utf-8').strip()

        # 检查内存使用率
        stdin, stdout, stderr = client.exec_command("free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'")
        memory_usage = stdout.read().decode('utf-8').strip()

        # 检查磁盘使用率
        stdin, stdout, stderr = client.exec_command("df -h | awk '$NF==\"/\"{printf \"%s\", $5}'")
        disk_usage = stdout.read().decode('utf-8').strip()

        # 检查负载
        stdin, stdout, stderr = client.exec_command("uptime | awk -F'[a-z]:' '{ print $2}'")
        load_average = stdout.read().decode('utf-8').strip()

        client.close()
        logger.info("Server health check completed.")

        return {
            "cpu_usage": float(cpu_usage),
            "memory_usage": float(memory_usage),
            "disk_usage": disk_usage,
            "load_average": float(load_average.split(",")[0])
        }
    except Exception as e:
        logger.error(f"Error checking server health: {e}")
        return None


def generate_alerts(server_metrics):
    """
    根据服务器指标生成警报。
    :param server_metrics: 服务器的健康指标字典
    :return: 警报列表
    """
    try:
        alerts = []
        if server_metrics.get("cpu_usage", 0) > 80:
            alerts.append("High CPU usage detected!")
        if server_metrics.get("memory_usage", 0) > 80:
            alerts.append("High memory usage detected!")
        if int(server_metrics.get("disk_usage", "0%").replace('%', '')) > 90:
            alerts.append("Disk usage is critically high!")
        if server_metrics.get("load_average", 0) > 5.0:
            alerts.append("High server load detected!")
        logger.info(f"Generated alerts: {alerts}")
        return alerts
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        return []


def analyze_server_load(load_data):
    """
    分析服务器负载数据。
    :param load_data: 服务器负载数据（如 '1.2, 2.5, 3.4'）
    :return: 分析结果字符串
    """
    try:
        load_values = [float(val) for val in load_data.split(",")]
        if any(load > 5.0 for load in load_values):
            logger.warning("High load detected on the server.")
            return "High load"
        logger.info("Server load is normal.")
        return "Normal load"
    except Exception as e:
        logger.error(f"Error analyzing server load: {e}")
        return "Error"


def analyze_all_server_loads():
    """
    分析所有服务器的平均负载。
    返回一个服务器负载统计的列表。
    """
    try:
        servers = Server.query.all()
        load_results = []

        for server in servers:
            # 查询服务器的平均负载
            avg_load = (
                MonitoringLog.query.filter_by(server_id=server.id)
                .with_entities(func.avg(MonitoringLog.value).label('avg_load'))
                .scalar()
            ) or 0  # 若没有记录，设置负载为 0

            load_results.append({
                "server_id": server.id,
                "ip": server.ip,
                "region": server.region,
                "average_load": round(avg_load, 2)  # 平均负载保留两位小数
            })
            logger.debug(f"Analyzed load for server {server.ip}: {avg_load}")

        return {"success": True, "data": load_results}
    except Exception as e:
        logger.error(f"Error analyzing server load: {str(e)}")
        return {"success": False, "message": f"Error analyzing server load: {str(e)}"}


def generate_system_alerts():
    """
    生成系统告警（如服务器过载）。
    """
    try:
        now = datetime.utcnow()

        # 获取最近 10 分钟内的监控数据
        recent_logs = MonitoringLog.query.filter(
            MonitoringLog.timestamp >= now - timedelta(minutes=10)
        ).all()

        new_alerts = []

        for log in recent_logs:
            if log.value > THRESHOLD:
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
                        server_id=log.server_id,  # 关联到具体服务器
                        resolved=False
                    )
                    new_alerts.append(alert)
                    logger.warning(f"Generated alert for server {log.server.ip} with load {log.value}")

        # 批量添加告警
        if new_alerts:
            db.session.add_all(new_alerts)

        db.session.commit()
        logger.info("Alerts generation completed.")
        return {"success": True, "message": "Alerts generated successfully."}

    except Exception as e:
        logger.error(f"Error generating alerts: {str(e)}")
        return {"success": False, "message": f"Error generating alerts: {str(e)}"}


# 导出模块
__all__ = [
    "check_server_health",
    "generate_alerts",
    "analyze_server_load",
    "analyze_all_server_loads",
    "generate_system_alerts"
]
