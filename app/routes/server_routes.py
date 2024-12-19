from flask import Blueprint, request, jsonify
from app.models import Server, User
from app import db

server_bp = Blueprint('server', __name__)

# 添加服务器
@server_bp.route('/api/add_server', methods=['POST'])
def add_server():
    """
    添加服务器
    请求参数:
        - ip: 服务器 IP 地址
        - region: 服务器所在地区
        - load: 当前服务器负载（可选，默认为 0.0）
    返回:
        - 成功或失败信息
    """
    data = request.json
    ip = data.get('ip')
    region = data.get('region')
    load = data.get('load', 0.0)

    # 检查参数是否完整
    if not ip or not region:
        return jsonify({"success": False, "message": "Missing required fields (ip or region)"}), 400

    # 检查服务器是否已经存在
    existing_server = Server.query.filter_by(ip=ip).first()
    if existing_server:
        return jsonify({"success": False, "message": "Server already exists"}), 400

    # 添加新服务器
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
    """
    添加用户与服务器的关联关系
    请求参数:
        - user_id: 用户 ID
        - server_id: 服务器 ID
    返回:
        - 成功或失败信息
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    # 检查参数是否完整
    if not user_id or not server_id:
        return jsonify({"success": False, "message": "Missing required fields (user_id or server_id)"}), 400

    # 查询用户和服务器是否存在
    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if not server:
        return jsonify({"success": False, "message": "Server not found"}), 404

    # 检查关联关系是否已经存在
    if server in user.servers:
        return jsonify({"success": False, "message": "User-Server relationship already exists"}), 400

    # 添加关联关系
    user.servers.append(server)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User-Server relationship added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
