import paramiko
import logging
from app.config import Config  # 引入 Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('docker_utils')


class DockerSSHManager:
    def __init__(self, ssh_host, ssh_user, ssh_key=None, ssh_password=None):
        """
        初始化 SSH 管理器。
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.ssh_password = ssh_password
        self.ssh_client = self._create_ssh_client()

    def _create_ssh_client(self):
        """
        创建并配置 SSH 客户端。
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.ssh_key:
                client.connect(self.ssh_host, username=self.ssh_user, key_filename=self.ssh_key)
            else:
                client.connect(self.ssh_host, username=self.ssh_user, password=self.ssh_password)
            logger.info("SSH connection established.")
            return client
        except Exception as e:
            logger.error(f"Error connecting to SSH: {e}")
            raise

    def execute_command(self, command, timeout=30):
        """
        执行远程命令并返回结果。
        """
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            error = stderr.read().decode('utf-8').strip()
            if error:
                logger.error(f"Command error: {error}")
                return None
            result = stdout.read().decode('utf-8').strip()
            return result
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return None

    def create_container(self, image_name, container_name, ports, environment=None):
        """
        在远程服务器上创建 Docker 容器。
        """
        command = f"docker run -d --name {container_name} -p {ports} "
        if environment:
            command += " ".join([f"-e {key}={value}" for key, value in environment.items()])
        command += f" {image_name}"
        return self.execute_command(command)

    def stop_container(self, container_name):
        """
        停止指定的 Docker 容器。
        """
        return self.execute_command(f"docker stop {container_name}")

    def get_container_status(self, container_name):
        """
        获取指定容器的状态。
        """
        return self.execute_command(f"docker inspect --format '{{{{.State.Status}}}}' {container_name}")

    def list_containers(self, all=False):
        """
        列出 Docker 容器。
        """
        command = f"docker ps {'-a' if all else ''} --format '{{{{.Names}}}}'"
        result = self.execute_command(command)
        return result.splitlines() if result else []

    def update_docker_container(self, container_name, new_image, environment=None, ports=None):
        """
        更新容器：停止、删除并重新创建。
        """
        try:
            self.stop_container(container_name)
            self.execute_command(f"docker rm {container_name}")
            return self.create_container(new_image, container_name, ports, environment)
        except Exception as e:
            logger.error(f"Error updating container {container_name}: {e}")
            return None

    def check_docker_health(self):
        """
        检查 Docker 的健康状态。
        """
        try:
            # 使用 Config 中的阈值配置（如果需要）
            threshold = Config.ALERT_THRESHOLD if hasattr(Config, 'ALERT_THRESHOLD') else 80.0

            # 检查 Docker 服务状态
            command = "systemctl is-active docker"
            result = self.execute_command(command)
            if result == "active":
                logger.info("Docker service is active.")
                return {"status": "healthy", "message": "Docker service is running", "threshold": threshold}
            else:
                logger.warning("Docker service is not running.")
                return {"status": "unhealthy", "message": "Docker service is not running"}
        except Exception as e:
            logger.error(f"Error checking Docker health: {e}")
            return {"status": "error", "message": f"Error checking Docker health: {e}"}

    def get_docker_traffic(self, container_name):
        """
        获取指定容器的流量数据。
        """
        try:
            # 示例命令：假设获取容器的网络流量
            command = f"docker stats {container_name} --no-stream --format '{{{{.NetIO}}}}'"
            result = self.execute_command(command)
            if result:
                # 示例解析结果
                rx, tx = result.split(" / ")
                return {"received": rx.strip(), "transmitted": tx.strip()}
            else:
                logger.error(f"Failed to fetch traffic for container {container_name}.")
                return {"error": "No data"}
        except Exception as e:
            logger.error(f"Error getting docker traffic: {e}")
            return {"error": str(e)}

    def close(self):
        """
        关闭 SSH 连接。
        """
        try:
            self.ssh_client.close()
            logger.info("SSH connection closed.")
        except Exception as e:
            logger.error(f"Error closing SSH connection: {e}")
            raise


# 独立函数包装
def create_container(ssh_host, ssh_user, ssh_password, image_name, container_name, ports, environment=None):
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.create_container(image_name, container_name, ports, environment)
    finally:
        manager.close()


def stop_container(ssh_host, ssh_user, ssh_password, container_name):
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.stop_container(container_name)
    finally:
        manager.close()


def get_container_status(ssh_host, ssh_user, ssh_password, container_name):
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.get_container_status(container_name)
    finally:
        manager.close()


def list_containers(ssh_host, ssh_user, ssh_password, all=False):
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.list_containers(all)
    finally:
        manager.close()


def update_docker_container(ssh_host, ssh_user, ssh_password, container_name, new_image, environment=None, ports=None):
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.update_docker_container(container_name, new_image, environment, ports)
    finally:
        manager.close()


def check_docker_health(ssh_host, ssh_user, ssh_password):
    """
    独立的检查 Docker 健康状态函数。
    """
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.check_docker_health()
    finally:
        manager.close()


def get_docker_traffic(ssh_host, ssh_user, ssh_password, container_name):
    """
    独立的获取 Docker 容器流量数据函数。
    """
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.get_docker_traffic(container_name)
    finally:
        manager.close()


def update_traffic_for_container(ssh_host, ssh_user, ssh_password, container_name, upload_traffic, download_traffic):
    """
    更新容器的上传和下载流量。
    """
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        # 获取当前的流量数据
        traffic = manager.get_docker_traffic(container_name)
        if "error" in traffic:
            logger.error(f"Failed to fetch traffic for container {container_name}.")
            return False
        
        # 更新流量数据
        current_upload = traffic["received"]
        current_download = traffic["transmitted"]

        # 将新的流量添加到当前流量
        new_upload_traffic = f"{float(current_upload) + upload_traffic}MB"
        new_download_traffic = f"{float(current_download) + download_traffic}MB"

        # 你可以根据需要更新数据库中的流量字段
        # 例如：DockerContainer.query.filter_by(container_id=container_name).update(...)

        logger.info(f"Updated traffic for container {container_name}: Upload: {new_upload_traffic}, Download: {new_download_traffic}")
        return True
    except Exception as e:
        logger.error(f"Error updating traffic for container {container_name}: {e}")
        return False
    finally:
        manager.close()


def delete_container_by_id(ssh_host, ssh_user, ssh_password, container_name):
    """
    删除指定的 Docker 容器。
    """
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        # 停止容器并删除
        manager.stop_container(container_name)
        manager.execute_command(f"docker rm {container_name}")
        logger.info(f"Container {container_name} deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Error deleting container {container_name}: {e}")
        return False
    finally:
        manager.close()


# 导出模块
__all__ = [
    "DockerSSHManager",
    "create_container",
    "stop_container",
    "get_container_status",
    "list_containers",
    "update_docker_container",
    "check_docker_health",
    "get_docker_traffic"
]
