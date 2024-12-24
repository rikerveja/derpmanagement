import paramiko
import logging
from app.config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('docker_utils')


class DockerSSHManager:
    def __init__(self, ssh_host, ssh_user, ssh_key=None, ssh_password=None):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.ssh_password = ssh_password
        self.ssh_client = self._create_ssh_client()

    def _create_ssh_client(self):
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

    def create_container(self, image_name, container_name, ports, environment=None):
        try:
            command = f"docker run -d --name {container_name} -p {ports} "
            if environment:
                command += " ".join([f"-e {key}={value}" for key, value in environment.items()])
            command += f" {image_name}"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                logger.error(f"Error creating container: {error}")
                return None
            container_id = stdout.read().decode('utf-8').strip()
            logger.info(f"Container created with ID: {container_id}")
            return container_id
        except Exception as e:
            logger.error(f"Error creating container via SSH: {e}")
            return None

    def stop_container(self, container_name):
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

    def update_container(self, container_name, new_image, environment=None, ports=None):
        """
        更新容器：停止、删除并重新创建。
        """
        try:
            # 停止容器
            self.stop_container(container_name)
            # 删除容器
            command = f"docker rm {container_name}"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                logger.error(f"Error removing container {container_name}: {error}")
                return None
            logger.info(f"Container {container_name} removed.")

            # 重新创建容器
            return self.create_container(new_image, container_name, ports, environment)
        except Exception as e:
            logger.error(f"Error updating container {container_name}: {e}")
            return None

    def close(self):
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


# 导出模块
__all__ = [
    "DockerSSHManager",
    "create_container",
    "stop_container",
    "get_container_status",
    "list_containers",
    "update_container"
]
