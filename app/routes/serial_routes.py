from flask import Blueprint, jsonify, request
from app.models import SerialNumber, db
import random
import string
from datetime import datetime, timedelta
import logging
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
        "duration_days": serial_number.duration_days,
        "created_at": serial_number.created_at.isoformat(),
        "expires_at": serial_number.expires_at.isoformat() if serial_number.expires_at else None,
        "expired": expired
    }), 200


# 生成序列号
@serial_bp.route('/api/serial/generate', methods=['POST'])
def generate_serial():
    """
    生成序列号
    """
    data = request.json
    count = data.get('count', 1)
    duration_days = data.get('duration_days', 30)
    serial_length = data.get('serial_length', 12)  # 序列号长度参数，默认12位

    # 参数验证
    if count <= 0 or duration_days <= 0 or serial_length <= 0:
        return jsonify({"success": False, "message": "Invalid parameters"}), 400

    serial_numbers = []
    for _ in range(count):
        # 确保序列号唯一性
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=serial_length))
            existing_serial = SerialNumber.query.filter_by(code=code).first()
            if not existing_serial:  # 如果序列号不重复，跳出循环
                break

        # 设置序列号的默认状态为 "unused"
        expires_at = datetime.utcnow() + timedelta(days=duration_days)
        serial_number = SerialNumber(code=code, duration_days=duration_days, status='unused', expires_at=expires_at)
        db.session.add(serial_number)
        serial_numbers.append(code)

    # 提交事务
    try:
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

