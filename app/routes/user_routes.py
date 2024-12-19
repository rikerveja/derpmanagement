from flask import Blueprint, request, jsonify
from app.models import User, UserHistory
from app.utils.auth_utils import hash_password, check_password, generate_jwt
from app.utils.email_utils import send_verification_email, validate_verification_code
from app import db
from app.utils.logging_utils import log_operation  # 引入统一日志记录工具
import logging

# 定义蓝图
user_bp = Blueprint('user', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加用户
@user_bp.route('/api/add_user', methods=['POST'])
def add_user():
    """
    用户注册接口
    请求参数：
        - username: 用户名
        - email: 用户邮箱
        - password: 密码
        - verification_code: 验证码
    返回：
        - 成功或失败信息
    """
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    verification_code = data.get('verification_code')

    # 检查字段是否完整
    if not username or not email or not password or not verification_code:
        log_operation(None, "add_user", "failed", "Missing required fields")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 验证邮箱验证码
    if not validate_verification_code(email, verification_code):
        log_operation(None, "add_user", "failed", f"Invalid or expired verification code for email: {email}")
        return jsonify({"success": False, "message": "Invalid or expired verification code"}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log_operation(None, "add_user", "failed", f"Email already registered: {email}")
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # 加密密码并创建新用户
    hashed_password = hash_password(password)
    user = User(username=username, email=email, password=hashed_password)

    db.session.add(user)
    try:
        db.session.commit()
        log_operation(user.id, "add_user", "success", f"User added successfully: {email}")
        return jsonify({"success": True, "message": "User added successfully", "user_id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(None, "add_user", "failed", f"Database error: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 用户登录
@user_bp.route('/api/login', methods=['POST'])
def login():
    """
    用户登录接口
    请求参数：
        - email: 用户邮箱
        - password: 用户密码
    返回：
        - 成功或失败信息，成功时返回 JWT 令牌
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # 检查字段是否完整
    if not email or not password:
        log_operation(None, "login", "failed", "Missing email or password")
        return jsonify({"success": False, "message": "Missing email or password"}), 400

    # 验证用户邮箱和密码
    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password):
        log_operation(None, "login", "failed", f"Invalid credentials for email: {email}")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    # 生成 JWT 令牌
    token = generate_jwt({"user_id": user.id})
    log_operation(user.id, "login", "success", f"Login successful for email: {email}")
    return jsonify({"success": True, "message": "Login successful", "token": token}), 200


# 发送邮箱验证码
@user_bp.route('/api/send_verification_email', methods=['POST'])
def send_verification_email_route():
    """
    发送邮箱验证码接口
    请求参数：
        - email: 用户邮箱
    返回：
        - 成功或失败信息
    """
    data = request.json
    email = data.get('email')

    # 检查邮箱是否提供
    if not email:
        log_operation(None, "send_verification_email", "failed", "Email is required")
        return jsonify({"success": False, "message": "Email is required"}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log_operation(None, "send_verification_email", "failed", f"Attempt to send verification code to registered email: {email}")
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # 发送验证码
    success = send_verification_email(email)
    if success:
        log_operation(None, "send_verification_email", "success", f"Verification email sent successfully to {email}")
        return jsonify({"success": True, "message": "Verification email sent successfully"}), 200

    log_operation(None, "send_verification_email", "failed", f"Failed to send verification email to {email}")
    return jsonify({"success": False, "message": "Failed to send email"}), 500


# 用户租赁信息展示
@user_bp.route('/api/user/rental_info', methods=['GET'])
def rental_info():
    """
    返回当前用户的租赁信息
    """
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    rental_info = {
        "username": user.username,
        "email": user.email,
        "rental_expiry": user.rental_expiry,
        "total_traffic": sum(container.upload_traffic + container.download_traffic for container in user.containers),
    }
    return jsonify({"success": True, "rental_info": rental_info}), 200


# 用户历史记录接口
@user_bp.route('/api/user/history/<int:user_id>', methods=['GET'])
def user_history(user_id):
    """
    获取用户租赁历史记录
    """
    history = UserHistory.query.filter_by(user_id=user_id).all()
    if not history:
        return jsonify({"success": False, "message": "No history found"}), 404

    history_data = [
        {
            "rental_start": record.rental_start,
            "rental_end": record.rental_end,
            "total_traffic": record.total_traffic,
        } for record in history
    ]
    return jsonify({"success": True, "history": history_data}), 200
