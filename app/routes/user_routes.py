from flask import Blueprint, request, jsonify
from app.models import User
from app.utils.auth import hash_password, check_password, generate_jwt
from app.utils.email_utils import send_verification_email, validate_verification_code
from app import db

user_bp = Blueprint('user', __name__)

# 添加用户
@user_bp.route('/api/add_user', methods=['POST'])
def add_user():
    # 用户注册逻辑
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    verification_code = data.get('verification_code')

    if not username or not email or not password or not verification_code:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    stored_code = validate_verification_code(email, verification_code)
    if not stored_code:
        return jsonify({"success": False, "message": "Invalid or expired verification code"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 400

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
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    token = generate_jwt({"user_id": user.id})
    return jsonify({"success": True, "message": "Login successful", "token": token}), 200


# 发送邮箱验证码
@user_bp.route('/api/send_verification_email', methods=['POST'])
def send_verification_email_route():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    success = send_verification_email(email)
    if success:
        return jsonify({"success": True, "message": "Verification email sent successfully"}), 200
    return jsonify({"success": False, "message": "Failed to send email"}), 500
