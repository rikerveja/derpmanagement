from flask import Blueprint, request, jsonify
from app.models import User
from app.utils.auth import hash_password, check_password, generate_jwt
from app.utils.email_utils import send_verification_email, validate_verification_code
from app import db

# 定义蓝图
user_bp = Blueprint('user', __name__)

# 添加用户
@user_bp.route('/api/add_user', methods=['POST'])
def add_user():
    """
    用户注册接口
    需要提供用户名、邮箱、密码、邮箱验证码
    """
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    verification_code = data.get('verification_code')

    # 检查字段是否完整
    if not username or not email or not password or not verification_code:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 验证邮箱验证码
    if not validate_verification_code(email, verification_code):
        return jsonify({"success": False, "message": "Invalid or expired verification code"}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # 加密密码并创建新用户
    hashed_password = hash_password(password)
    user = User(username=username, email=email, password=hashed_password)

    db.session.add(user)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User added successfully", "user_id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 用户登录
@user_bp.route('/api/login', methods=['POST'])
def login():
    """
    用户登录接口
    需要提供邮箱和密码
    返回 JWT 令牌
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # 检查字段是否完整
    if not email or not password:
        return jsonify({"success": False, "message": "Missing email or password"}), 400

    # 验证用户邮箱和密码
    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # 生成 JWT 令牌
    token = generate_jwt({"user_id": user.id})
    return jsonify({"success": True, "message": "Login successful", "token": token}), 200


# 发送邮箱验证码
@user_bp.route('/api/send_verification_email', methods=['POST'])
def send_verification_email_route():
    """
    发送邮箱验证码接口
    需要提供用户的邮箱地址
    """
    data = request.json
    email = data.get('email')

    # 检查邮箱是否提供
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    # 发送验证码
    success = send_verification_email(email)
    if success:
        return jsonify({"success": True, "message": "Verification email sent successfully"}), 200
    return jsonify({"success": False, "message": "Failed to send email"}), 500
