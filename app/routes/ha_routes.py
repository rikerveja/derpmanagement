from flask import Blueprint, jsonify
from app.models import Server

ha_bp = Blueprint('ha', __name__)

@ha_bp.route('/load_balancing', methods=['GET'])
def load_balancing():
    """
    ��ȡ���з������ĸ�����Ϣ
    """
    servers = Server.query.all()
    server_loads = [
        {"server_id": server.id, "ip": server.ip, "region": server.region, "load": server.load}
        for server in servers
    ]
    return jsonify({"success": True, "servers": server_loads}), 200
