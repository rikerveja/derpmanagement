import docker
import logging
from docker.errors import DockerException

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('docker_utils')

class DockerManager:
    def __init__(self):
        # 创建 docker 客户端实例
        self.client = docker.from_env()

    def create_container(self, image_name, container_name, ports, environment=None):
        """
        创建并启动一个 Docker 容器。
        """
        try:
            container = self.client.containers.run(
                image=image_name,
                name=container_name,
                ports=ports,
                environment=environment,
                detach=True
            )
            logger.info(f"Container {container_name} created and started.")
            return container
        except DockerException as e:
            logger.error(f"Error creating container {container_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating container {container_name}: {e}")
            return None

    def stop_container(self, container_name):
        """
        停止一个正在运行的容器。
        """
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            logger.info(f"Container {container_name} stopped.")
            return True
        except DockerException as e:
            logger.error(f"Error stopping container {container_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error stopping container {container_name}: {e}")
            return False

    def get_container_status(self, container_name):
        """
        获取容器的状态。
        """
        try:
            container = self.client.containers.get(container_name)
            return container.status
        except DockerException as e:
            logger.error(f"Error getting status for container {container_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting status for container {container_name}: {e}")
            return None

    def list_containers(self, all=False):
        """
        列出所有容器（包括已停止的容器）。
        """
        try:
            containers = self.client.containers.list(all=all)
            return containers
        except DockerException as e:
            logger.error(f"Error listing containers: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing containers: {e}")
            return []

# 使用 DockerManager 管理容器
docker_manager = DockerManager()

# 示例：创建容器
docker_manager.create_container(
    image_name="nginx",
    container_name="my_nginx_container",
    ports={'80/tcp': 8080}
)

# 示例：停止容器
docker_manager.stop_container("my_nginx_container")
