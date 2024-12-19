import logging
import requests

logging.basicConfig(level=logging.INFO)

def get_server_status(ip):
    """
    获取服务器状态
    """
    try:
        response = requests.get(f"http://{ip}/health")
        if response.status_code == 200:
            return {"status": "healthy", "details": response.json()}
        else:
            return {"status": "unhealthy", "details": response.text}
    except Exception as e:
        logging.error(f"Failed to get server status for {ip}: {e}")
        return {"status": "unreachable", "error": str(e)}

def monitor_server_health():
    """
    批量监控所有服务器健康
    """
    from app.models import Server
    servers = Server.query.all()
    results = []

    for server in servers:
        status = get_server_status(server.ip)
        results.append({"server_id": server.id, "ip": server.ip, "status": status})
        logging.info(f"Server {server.ip} status: {status}")

    return results
