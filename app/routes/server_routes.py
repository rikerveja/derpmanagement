from flask import Blueprint, request, jsonify
from app.models import Server, User
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
        return jsonify({"success": False, "message": "Missing required fields"}), 400

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


# 添加用户与服务器的关联关系
@server_bp.route('/api/add_user_server', methods=['POST'])
def add_user_server():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    if server in user.servers:
        return jsonify({"success": False, "message": "User-Server relationship already exists"}), 400

    user.servers.append(server)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User-Server relationship added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
