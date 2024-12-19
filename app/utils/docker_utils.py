import docker
import logging

logging.basicConfig(level=logging.INFO)

client = docker.from_env()

def create_container(image, name, ports, environment=None):
    """
    创建 Docker 容器
    """
    try:
        container = client.containers.run(
            image=image,
            name=name,
            ports=ports,
            environment=environment,
            detach=True
        )
        logging.info(f"Container {name} created successfully.")
        return container
    except Exception as e:
        logging.error(f"Failed to create container {name}: {e}")
        return None

def stop_container(container_name):
    """
    停止并删除容器
    """
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
        logging.info(f"Container {container_name} stopped and removed.")
    except Exception as e:
        logging.error(f"Failed to stop/remove container {container_name}: {e}")

def get_container_status(container_name):
    """
    获取容器状态
    """
    try:
        container = client.containers.get(container_name)
        status = container.status
        logging.info(f"Container {container_name} status: {status}")
        return status
    except docker.errors.NotFound:
        logging.error(f"Container {container_name} not found.")
        return "not_found"
    except Exception as e:
        logging.error(f"Failed to get container status for {container_name}: {e}")
        return "error"

def list_containers():
    """
    列出所有容器
    """
    try:
        containers = client.containers.list(all=True)
        container_info = [{"id": container.id, "name": container.name, "status": container.status} for container in containers]
        logging.info(f"Listed {len(containers)} containers.")
        return container_info
    except Exception as e:
        logging.error(f"Failed to list containers: {e}")
        return []
