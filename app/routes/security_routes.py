from flask import Blueprint, jsonify, request
from app.models import User, db
import logging

# 定义蓝图
security_bp = Blueprint('security', __name__)
logging.basicConfig(level=logging.INFO)

@security_bp.route('/api/security/bind_device', methods=['POST'])
def bind_device():
    """
    绑定设备到用户账户
    请求参数：
    - user_id: 用户 ID
    - device_id: 设备 ID
    """
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id')

    if not user_id or not device_id:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # 模拟绑定逻辑
    logging.info(f"Device {device_id} bound to user {user_id}")
    return jsonify({"success": True, "message": f"Device {device_id} successfully bound to user {user_id}"}), 200

@security_bp.route('/api/security/unbind_device', methods=['POST'])
def unbind_device():
    """
    解绑设备
    请求参数：
    - user_id: 用户 ID
    - device_id: 设备 ID
    """
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id')

    if not user_id or not device_id:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # 模拟解绑逻辑
    logging.info(f"Device {device_id} unbound from user {user_id}")
    return jsonify({"success": True, "message": f"Device {device_id} successfully unbound from user {user_id}"}), 200

@security_bp.route('/api/security/check_bindings/<int:user_id>', methods=['GET'])
def check_bindings(user_id):
    """
    检查用户的设备绑定状态
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # 模拟设备绑定列表
    bindings = [{"device_id": "device_12345", "status": "active"}]  # 示例数据
    return jsonify({"success": True, "bindings": bindings}), 200
