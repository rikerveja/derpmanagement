import logging
import requests
from app.models import Server

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_server_status(ip):
    """
    获取服务器状态
    :param ip: 服务器 IP 地址
    :return: 返回服务器状态信息，包括健康状态和详细信息
    """
    try:
        # 发送请求获取健康状态
        response = requests.get(f"http://{ip}/health")
        if response.status_code == 200:
            logger.info(f"Server {ip} is healthy.")
            return {"status": "healthy", "details": response.json()}
        else:
            logger.warning(f"Server {ip} is unhealthy. Status code: {response.status_code}")
            return {"status": "unhealthy", "details": response.text}
    except requests.exceptions.RequestException as e:
        # 捕获所有请求异常，如网络问题、超时等
        logger.error(f"Failed to get server status for {ip}: {str(e)}")
        return {"status": "unreachable", "error": str(e)}

def monitor_server_health():
    """
    批量监控所有服务器健康状态
    :return: 服务器健康状态的列表
    """
    results = []

    try:
        servers = Server.query.all()  # 查询所有服务器
        if not servers:
            logger.warning("No servers found for health check.")
            return {"success": False, "message": "No servers found for health check."}

        for server in servers:
            status = get_server_status(server.ip)
            results.append({
                "server_id": server.id,
                "ip": server.ip,
                "status": status
            })
            logger.info(f"Server {server.ip} status: {status}")

        return {"success": True, "data": results}

    except Exception as e:
        logger.error(f"Error monitoring server health: {str(e)}")
        return {"success": False, "message": f"Error monitoring server health: {str(e)}"}
