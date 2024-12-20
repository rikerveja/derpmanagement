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
    except Exception as e:
        logging.error(f"Failed to get status for container {container_name}: {e}")
        return None

def list_containers(all=False):
    """
    列出容器
    """
    try:
        containers = client.containers.list(all=all)
        container_list = [{'name': c.name, 'status': c.status} for c in containers]
        logging.info(f"Retrieved container list: {container_list}")
        return container_list
    except Exception as e:
        logging.error(f"Failed to list containers: {e}")
        return []
