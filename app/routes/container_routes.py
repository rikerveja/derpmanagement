from flask import Blueprint, request, jsonify
from app.utils.docker_utils import create_container, stop_container, get_container_status, list_containers

container_bp = Blueprint('container', __name__)

@container_bp.route('/api/containers', methods=['GET'])
def get_containers():
    all_containers = request.args.get('all', 'false').lower() == 'true'
    containers = list_containers(all=all_containers)
    container_list = [{'id': c.id, 'name': c.name, 'status': c.status} for c in containers]
    return jsonify({"success": True, "containers": container_list}), 200

@container_bp.route('/api/containers', methods=['POST'])
def create_new_container():
    data = request.json
    image_name = data.get('image_name')
    container_name = data.get('container_name')
    ports = data.get('ports')
    environment = data.get('environment', None)

    if not image_name or not container_name or not ports:
        return jsonify({"success": False, "message": "Missing required parameters"}), 400

    container = create_container(image_name, container_name, ports, environment)
    if container:
        return jsonify({"success": True, "message": f"Container {container_name} created successfully"}), 201
    else:
        return jsonify({"success": False, "message": "Failed to create container"}), 500

@container_bp.route('/api/containers/<container_name>/stop', methods=['POST'])
def stop_existing_container(container_name):
    result = stop_container(container_name)
    if result:
        return jsonify({"success": True, "message": f"Container {container_name} stopped successfully"}), 200
    else:
        return jsonify({"success": False, "message": f"Failed to stop container {container_name}"}), 500

@container_bp.route('/api/containers/<container_name>/status', methods=['GET'])
def get_container_status_route(container_name):
    status = get_container_status(container_name)
    if status:
        return jsonify({"success": True, "container_name": container_name, "status": status}), 200
    else:
        return jsonify({"success": False, "message": f"Failed to retrieve status for container {container_name}"}), 500
