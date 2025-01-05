from flask import Blueprint, jsonify, request  # 添加 Blueprint 导入
from datetime import datetime, timedelta
import random
import string
import logging
from app.models import SerialNumber
from app import db
import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 初始化 Flask-Limiter
limiter = Limiter(get_remote_address)

# 初始化 Redis 客户端
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 定义蓝图
serial_bp = Blueprint('serial', __name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 配置限流，每分钟最多 5 次请求
@limiter.limit("5 per minute")
@serial_bp.route('/api/serial/check/<serial_code>', methods=['GET'])
def check_serial(serial_code):
    """
    检查序列号状态，并侦测暴力猜测行为
    """
    ip_address = request.remote_addr
    
    # 检查暴力行为
    if is_suspected_brute_force(ip_address):
        log_operation(None, "check_serial", "failed", f"Brute force attempt detected from IP: {ip_address}")
        return jsonify({"success": False, "message": "Too many failed attempts. You are temporarily banned."}), 403
    
    try:
        # 查找序列号
        serial_number = SerialNumber.query.filter_by(code=serial_code).first()
        if not serial_number:
            log_failed_attempt(ip_address)
            return jsonify({"success": False, "message": "Serial number not found"}), 404

        # 检查序列号是否过期
        current_time = datetime.utcnow()
        expired = serial_number.expires_at < current_time if serial_number.expires_at else False

        # 返回序列号的详细信息
        return jsonify({
            "success": True,
            "serial_code": serial_number.code,
            "status": serial_number.status,
            "duration_days": serial_number.valid_days,
            "created_at": serial_number.created_at.isoformat(),
            "expires_at": serial_number.expires_at.isoformat() if serial_number.expires_at else None,
            "expired": expired
        }), 200
    except Exception as e:
        logging.error(f"Error checking serial code {serial_code}: {str(e)}")
        return jsonify({"success": False, "message": f"Error checking serial code: {str(e)}"}), 500


# 生成序列号
@serial_bp.route('/api/serial/generate', methods=['POST'])
def generate_serial():
    """
    生成序列号
    """
    data = request.json
    count = data.get('count', 1)
    valid_days = data.get('valid_days', 30)
    prefix = data.get('prefix', '')  # 序列号的前半部分

    # 序列号后半部分长度
    serial_length = 6

    # 参数验证
    if count <= 0 or valid_days <= 0 or serial_length <= 0:
        return jsonify({"success": False, "message": "Invalid parameters"}), 400

    serial_numbers = []
    activated_at = datetime.utcnow()  # 获取当前时间，作为 activated_at
    start_date = activated_at  # 激活时间作为起始时间
    end_date = start_date + timedelta(days=valid_days)  # 过期时间 = 激活时间 + 有效天数

    try:
        for _ in range(count):
            # 确保序列号唯一性
            while True:
                # 拼接前半部分和后半部分（6位随机字符）
                suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=serial_length))
                code = prefix + suffix  # 完整序列号

                # 检查序列号是否唯一
                existing_serial = SerialNumber.query.filter_by(code=code).first()
                if not existing_serial:  # 如果序列号不重复，跳出循环
                    break

            # 创建新的序列号对象并加入数据库
            serial_number = SerialNumber(
                code=code,
                status='unused',  # 默认状态为 "unused"
                valid_days=valid_days,
                start_date=start_date,
                end_date=end_date,
                activated_at=activated_at,
                expires_at=end_date
            )
            db.session.add(serial_number)
            serial_numbers.append(code)  # 将生成的序列号加入返回的列表

        # 提交事务
        db.session.commit()
        logging.info(f"Generated {count} serial numbers successfully.")
        return jsonify({"success": True, "serial_numbers": serial_numbers}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error generating serial numbers: {e}")
        return jsonify({"success": False, "message": f"Error generating serial numbers: {str(e)}"}), 500


# 检测暴力猜解行为
def is_suspected_brute_force(ip_address):
    """
    判断某个 IP 地址是否发生暴力猜解行为
    """
    failed_attempts = redis_client.get(f"failed_attempts:{ip_address}")
    if failed_attempts and int(failed_attempts) > 5:  # 超过 5 次失败尝试
        return True
    return False

def log_failed_attempt(ip_address):
    """
    记录每次失败的尝试
    """
    redis_client.incr(f"failed_attempts:{ip_address}")
    redis_client.expire(f"failed_attempts:{ip_address}", 300)  # 设置 5 分钟过期时间


# 用户封禁或删除
def ban_user(user_id):
    """
    临时封禁用户的功能（可进一步扩展）
    """
    user = User.query.get(user_id)
    if user:
        user.is_banned = True
        db.session.commit()
        logging.info(f"User {user_id} has been banned")


# 更新序列号
@serial_bp.route('/api/serial/update/<int:id>', methods=['PUT'])
def update_serial_number(id):
    """
    更新指定序列号的状态和过期时间
    :param id: 序列号 ID
    """
    data = request.json
    status = data.get('status')
    expires_at = data.get('expires_at')

    serial = SerialNumber.query.get(id)
    if not serial:
        return jsonify({"success": False, "message": "Serial number not found"}), 404

    try:
        serial.status = status if status else serial.status
        serial.expires_at = expires_at if expires_at else serial.expires_at
        db.session.commit()
        return jsonify({"success": True, "message": "Serial number updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating serial number: {e}")
        return jsonify({"success": False, "message": f"Error updating serial number: {str(e)}"}), 500


# 删除序列号
@serial_bp.route('/api/serial/delete/<int:id>', methods=['DELETE'])
def delete_serial_number(id):
    """
    删除指定序列号
    :param id: 序列号 ID
    """
    serial = SerialNumber.query.get(id)
    if not serial:
        return jsonify({"success": False, "message": "Serial number not found"}), 404

    try:
        db.session.delete(serial)
        db.session.commit()
        return jsonify({"success": True, "message": "Serial number deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting serial number: {e}")
        return jsonify({"success": False, "message": f"Error deleting serial number: {str(e)}"}), 500
