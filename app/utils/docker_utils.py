import paramiko
import logging
from app.config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('docker_utils')

class DockerSSHManager:
    def __init__(self, ssh_host, ssh_user, ssh_key=None, ssh_password=None):
        """
        初始化 SSH 连接配置。
        :param ssh_host: 远程主机的 IP 地址或域名
        :param ssh_user: SSH 用户名
        :param ssh_key: 私钥文件路径（可选）
        :param ssh_password: SSH 密码（可选）
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.ssh_password = ssh_password
        self.ssh_client = self._create_ssh_client()

    def _create_ssh_client(self):
        """创建 SSH 客户端"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥（生产环境应配置为更严格的策略）

            if self.ssh_key:
                client.connect(self.ssh_host, username=self.ssh_user, key_filename=self.ssh_key)
            else:
                client.connect(self.ssh_host, username=self.ssh_user, password=self.ssh_password)

            logger.info("SSH connection established.")
            return client
        except Exception as e:
            logger.error(f"Error connecting to SSH: {e}")
            raise  # 重新抛出异常，以便上层处理

    def create_container(self, image_name, container_name, ports, environment=None):
        """
        通过 SSH 在远程服务器上创建 Docker 容器。
        """
        try:
            # Docker 命令
            command = f"docker run -d --name {container_name} -p {ports} "
            if environment:
                command += " ".join([f"-e {key}={value}" for key, value in environment.items()])

            command += f"{image_name}"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                logger.error(f"Error creating container: {error}")
                return None
            container_id = stdout.read().decode('utf-8').strip()  # 获取容器 ID
            logger.info(f"Container created with ID: {container_id}")
            return container_id
        except Exception as e:
            logger.error(f"Error creating container via SSH: {e}")
            return None

    def stop_container(self, container_name):
        """
        通过 SSH 停止远程服务器上的 Docker 容器。
        """
        try:
            command = f"docker stop {container_name}"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                logger.error(f"Error stopping container {container_name}: {error}")
                return False
            logger.info(f"Container {container_name} stopped.")
            return True
        except Exception as e:
            logger.error(f"Error stopping container via SSH: {e}")
            return False

    def get_container_status(self, container_name):
        """
        获取远程服务器上 Docker 容器的状态。
        """
        try:
            command = f"docker inspect --format '{{{{.State.Status}}}}' {container_name}"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                logger.error(f"Error getting status for container {container_name}: {error}")
                return None
            status = stdout.read().decode('utf-8').strip()
            logger.info(f"Container {container_name} status: {status}")
            return status
        except Exception as e:
            logger.error(f"Error getting container status via SSH: {e}")
            return None

    def list_containers(self, all=False):
        """
        列出远程服务器上的 Docker 容器。
        """
        try:
            command = f"docker ps {'-a' if all else ''}"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                logger.error(f"Error listing containers: {error}")
                return []
            containers = stdout.read().decode('utf-8').splitlines()
            logger.info(f"Containers listed: {containers}")
            return containers
        except Exception as e:
            logger.error(f"Error listing containers via SSH: {e}")
            return []

    def close(self):
        """关闭 SSH 客户端连接"""
        try:
            self.ssh_client.close()
            logger.info("SSH connection closed.")
        except Exception as e:
            logger.error(f"Error closing SSH connection: {e}")
            raise
