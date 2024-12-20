import docker
from docker.errors import DockerException

def create_container(image_name, container_name, ports, environment=None):
    try:
        client = docker.from_env()
        container = client.containers.run(
            image=image_name,
            name=container_name,
            ports=ports,
            environment=environment,
            detach=True
        )
        return container
    except DockerException as e:
        print(f"Error creating container: {e}")
        return None

def stop_container(container_name):
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.stop()
        return True
    except DockerException as e:
        print(f"Error stopping container: {e}")
        return False

def get_container_status(container_name):
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        return container.status
    except DockerException as e:
        print(f"Error getting container status: {e}")
        return None

def list_containers(all=False):
    try:
        client = docker.from_env()
        containers = client.containers.list(all=all)
        return containers
    except DockerException as e:
        print(f"Error listing containers: {e}")
        return []
