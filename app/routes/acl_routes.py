# app/routes/acl_routes.py
from flask import Blueprint, request, jsonify
from app.models import ACLConfig, User, Server
from app import db
from datetime import datetime, timedelta

acl_bp = Blueprint('acl', __name__)

# 动态生成 ACL 配置
@acl_bp.route('/api/generate_acl', methods=['POST'])
def generate_acl():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')
    duration_days = data.get('duration_days', 30)  # 默认有效期 30 天

    user = User.query.get(user_id)
    server = Server.query.get(server_id)
    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    # 模拟生成 ACL 配置
    acl_data = f"# ACL for User {user_id} on Server {server_id}\nallow-all"

    # 创建 ACLConfig 对象
    expires_at = datetime.utcnow() + timedelta(days=duration_days)
    acl = ACLConfig(user_id=user_id, server_id=server_id, config_data=acl_data, expires_at=expires_at)
    db.session.add(acl)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "ACL generated successfully", "acl_id": acl.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
