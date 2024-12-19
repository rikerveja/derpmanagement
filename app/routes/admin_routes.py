from flask import Blueprint, jsonify, request
from app.models import User
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/permissions/<int:user_id>', methods=['POST'])
def set_user_permissions(user_id):
    """
    设置用户权限
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    data = request.json
    role = data.get('role')
    if role not in ['admin', 'user']:
        return jsonify({"success": False, "message": "Invalid role"}), 400

    user.role = role
    db.session.commit()
    return jsonify({"success": True, "message": f"Role updated to {role}"}), 200
