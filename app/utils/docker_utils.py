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

    def update_container(self, container_name, new_image, environment=None, ports=None):
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


def update_container(ssh_host, ssh_user, ssh_password, container_name, new_image, environment=None, ports=None):
    manager = DockerSSHManager(ssh_host, ssh_user, ssh_password=ssh_password)
    try:
        return manager.update_container(container_name, new_image, environment, ports)
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


# 导出模块
__all__ = [
    "DockerSSHManager",
    "create_container",
    "stop_container",
    "get_container_status",
    "list_containers",
    "update_container",
    "check_docker_health"
]
