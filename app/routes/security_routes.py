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
        logging.error("Missing required fields: user_id or device_id")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found")
            return jsonify({"success": False, "message": "User not found"}), 404

        # 模拟绑定逻辑
        logging.info(f"Device {device_id} bound to user {user_id}")
        # 这里可以加入数据库或其他操作，例如将设备 ID 存入数据库

        return jsonify({"success": True, "message": f"Device {device_id} successfully bound to user {user_id}"}), 200
    except Exception as e:
        logging.error(f"Error binding device: {str(e)}")
        return jsonify({"success": False, "message": f"Error binding device: {str(e)}"}), 500


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
        logging.error("Missing required fields: user_id or device_id")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found")
            return jsonify({"success": False, "message": "User not found"}), 404

        # 模拟解绑逻辑
        logging.info(f"Device {device_id} unbound from user {user_id}")
        # 这里可以加入数据库或其他操作，例如从数据库中删除设备绑定记录

        return jsonify({"success": True, "message": f"Device {device_id} successfully unbound from user {user_id}"}), 200
    except Exception as e:
        logging.error(f"Error unbinding device: {str(e)}")
        return jsonify({"success": False, "message": f"Error unbinding device: {str(e)}"}), 500


@security_bp.route('/api/security/check_bindings/<int:user_id>', methods=['GET'])
def check_bindings(user_id):
    """
    检查用户的设备绑定状态
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found")
            return jsonify({"success": False, "message": "User not found"}), 404

        # 模拟设备绑定列表
        # 在实际应用中，应该从数据库中查询用户绑定的设备
        bindings = [{"device_id": "device_12345", "status": "active"}]  # 示例数据

        return jsonify({"success": True, "bindings": bindings}), 200
    except Exception as e:
        logging.error(f"Error checking device bindings for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error checking device bindings: {str(e)}"}), 500
