from flask import Blueprint, jsonify, request
import json
import os
from app.models import User, Server
from datetime import datetime, timedelta

acl_bp = Blueprint('acl', __name__)

# 临时存储 ACL 配置（生产环境建议存入数据库）
acl_store = {}

@acl_bp.route('/generate', methods=['POST'])
def generate_acl():
    """
    动态生成用户 ACL 配置
    """
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # 模拟绑定三台服务器，动态生成 ACL 配置
    servers = Server.query.limit(3).all()
    acl = {
        "user_id": user.id,
        "device_id": device_id,
        "servers": [{"ip": server.ip, "region": server.region} for server in servers],
        "expires_at": (datetime.utcnow() + timedelta(days=32)).isoformat()
    }

    # 保存到临时存储
    acl_store[user_id] = acl
    return jsonify({"success": True, "acl": acl}), 200


@acl_bp.route('/update/<int:user_id>', methods=['POST'])
def update_acl(user_id):
    """
    管理员手动更新 ACL 配置
    """
    acl = acl_store.get(user_id)
    if not acl:
        return jsonify({"success": False, "message": "ACL not found for user"}), 404

    acl["expires_at"] = (datetime.utcnow() + timedelta(days=32)).isoformat()
    acl_store[user_id] = acl
    return jsonify({"success": True, "message": "ACL updated successfully", "acl": acl}), 200


@acl_bp.route('/fetch/<int:user_id>', methods=['GET'])
def fetch_acl(user_id):
    """
    获取用户 ACL 配置
    """
    acl = acl_store.get(user_id)
    if not acl:
        return jsonify({"success": False, "message": "ACL not found for user"}), 404
    return jsonify({"success": True, "acl": acl}), 200
