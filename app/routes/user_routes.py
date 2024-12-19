from flask import Blueprint, request, jsonify
from app.models import User
from app.utils.auth import hash_password, check_password, generate_jwt
from app.utils.email_utils import send_verification_email, validate_verification_code
from app import db
from app.utils.log_utils import log_operation  # 引入统一日志记录工具
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
        log_operation("add_user", "Missing required fields", "ERROR")
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 验证邮箱验证码
    if not validate_verification_code(email, verification_code):
        log_operation("add_user", f"Invalid or expired verification code for email: {email}", "WARNING")
        return jsonify({"success": False, "message": "Invalid or expired verification code"}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log_operation("add_user", f"Email already registered: {email}", "WARNING")
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # 加密密码并创建新用户
    hashed_password = hash_password(password)
    user = User(username=username, email=email, password=hashed_password)

    db.session.add(user)
    try:
        db.session.commit()
        log_operation("add_user", f"User added successfully: {email}", "INFO")
        return jsonify({"success": True, "message": "User added successfully", "user_id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        log_operation("add_user", f"Database error while adding user: {e}", "ERROR")
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
        log_operation("login", "Missing email or password", "ERROR")
        return jsonify({"success": False, "message": "Missing email or password"}), 400

    # 验证用户邮箱和密码
    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password):
        log_operation("login", f"Invalid login attempt for email: {email}", "WARNING")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    # 生成 JWT 令牌
    token = generate_jwt({"user_id": user.id})
    log_operation("login", f"Login successful for email: {email}", "INFO")
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
        log_operation("send_verification_email", "Email is required", "ERROR")
        return jsonify({"success": False, "message": "Email is required"}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log_operation("send_verification_email", f"Attempt to send verification code to registered email: {email}", "WARNING")
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # 发送验证码
    success = send_verification_email(email)
    if success:
        log_operation("send_verification_email", f"Verification email sent successfully to {email}", "INFO")
        return jsonify({"success": True, "message": "Verification email sent successfully"}), 200

    log_operation("send_verification_email", f"Failed to send verification email to {email}", "ERROR")
    return jsonify({"success": False, "message": "Failed to send email"}), 500
