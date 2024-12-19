from flask import Blueprint, request, jsonify
from app.models import Server, User
from app.utils.server_utils import get_server_status, monitor_server_health
from app.utils.notifications_utils import send_general_notification
from app import db

server_bp = Blueprint('server', __name__)

# 添加服务器
@server_bp.route('/api/add_server', methods=['POST'])
def add_server():
    data = request.json
    ip = data.get('ip')
    region = data.get('region')
    load = data.get('load', 0.0)

    if not ip or not region:
        return jsonify({"success": False, "message": "Missing required fields (ip or region)"}), 400

    existing_server = Server.query.filter_by(ip=ip).first()
    if existing_server:
        return jsonify({"success": False, "message": "Server already exists"}), 400

    server = Server(ip=ip, region=region, load=load)
    db.session.add(server)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Server added successfully", "server_id": server.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# 获取服务器状态
@server_bp.route('/api/server/status/<int:server_id>', methods=['GET'])
def server_status(server_id):
    server = Server.query.get(server_id)
    if not server:
        return jsonify({"success": False, "message": "Server not found"}), 404

    status = get_server_status(server.ip)
    return jsonify({"success": True, "status": status}), 200

# 监控服务器健康
@server_bp.route('/api/server/health_check', methods=['GET'])
def health_check():
    try:
        results = monitor_server_health()
        return jsonify({"success": True, "health_check_results": results}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error during health check: {str(e)}"}), 500
