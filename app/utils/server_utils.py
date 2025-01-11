import logging
import subprocess
from app.models import Server

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ping_server(ip_address):
    """
    使用 ping 命令检测服务器是否可达
    :param ip_address: 服务器 IP 地址
    :return: 返回服务器是否可达的状态（reachable 或 unreachable）和详细错误信息
    """
    try:
        # 执行 ping 命令
        result = subprocess.run(
            ['ping', '-c', '4', ip_address], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if result.returncode == 0:
            return "reachable", ""
        else:
            return "unreachable", result.stderr
    except Exception as e:
        return "unreachable", str(e)

def monitor_server_health():
    """
    批量监控所有服务器健康状态，使用 ping 检测
    :return: 服务器健康状态的列表
    """
    results = []

    try:
        servers = Server.query.all()  # 查询所有服务器
        if not servers:
            logger.warning("No servers found for health check.")
            return {"success": False, "message": "No servers found for health check."}

        for server in servers:
            # 使用 ping 检测服务器是否可达
            status, error = ping_server(server.ip_address)
            results.append({
                "server_id": server.id,
                "ip_address": server.ip_address,
                "status": {"status": status, "error": error if status == "unreachable" else ""}
            })
            logger.info(f"Server {server.ip_address} status: {status}")

        return {"success": True, "data": results}

    except Exception as e:
        logger.error(f"Error monitoring server health: {str(e)}")
        return {"success": False, "message": f"Error monitoring server health: {str(e)}"}
