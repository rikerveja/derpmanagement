from flask import Blueprint, jsonify, request
from app.models import User
from app import db
from app.utils.logging_utils import log_operation  # 引入日志记录工具

# 定义蓝图
admin_bp = Blueprint('admin', __name__)

# 定义支持的角色
VALID_ROLES = ['admin', 'user', 'super_admin', 'distributor']

@admin_bp.route('/permissions/<int:user_id>', methods=['POST'])
def set_user_permissions(user_id):
    """
    设置用户权限
    """
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        log_operation(user_id=None, operation="set_user_permissions", status="failed", details="User not found")
        return jsonify({"success": False, "message": "User not found"}), 404

    # 获取请求数据
    data = request.json
    role = data.get('role')

    # 验证角色是否合法
    if not role or role not in VALID_ROLES:
        log_operation(user_id=user_id, operation="set_user_permissions", status="failed", details="Invalid role")
        return jsonify({"success": False, "message": "Invalid role"}), 400

    # 仅允许超级管理员修改用户角色
    # 检查是否为超级管理员，并且只有超级管理员可以赋予超级管理员权限
    if role == 'super_admin' and user.role != 'super_admin':
        log_operation(user_id=user_id, operation="set_user_permissions", status="failed", details="Unauthorized access")
        return jsonify({"success": False, "message": "You do not have permission to assign this role"}), 403

    if role == 'distributor' and user.role == 'super_admin':
        log_operation(user_id=user_id, operation="set_user_permissions", status="failed", details="Super Admin cannot be a distributor")
        return jsonify({"success": False, "message": "Super Admin cannot be a distributor"}), 403

    # 修改角色并保存
    old_role = user.role
    user.role = role

    try:
        db.session.commit()

        # 记录操作日志
        log_operation(user_id=user_id, operation="set_user_permissions", status="success", details=f"Role updated from {old_role} to {role}")
        return jsonify({"success": True, "message": f"Role updated to {role}"}), 200
    except Exception as e:
        db.session.rollback()  # 回滚事务
        log_operation(user_id=user_id, operation="set_user_permissions", status="failed", details=f"Database error: {str(e)}")
        return jsonify({"success": False, "message": "Failed to update role due to a database error"}), 500
