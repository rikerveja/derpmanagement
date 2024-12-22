from flask import Blueprint, request, jsonify, send_from_directory
from app.models import User, UserHistory
from app.utils.auth_utils import hash_password, check_password, generate_jwt, generate_refresh_token
from app.utils.email_utils import send_verification_email, validate_verification_code
from app import db
from app.utils.logging_utils import log_operation  # 引入统一日志记录工具
import logging
import os

# 定义蓝图
user_bp = Blueprint('user', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 验证必填字段
def validate_required_fields(data, fields):
    missing_fields = [field for field in fields if not data.get(field)]
    return missing_fields

# 添加用户
@user_bp.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    required_fields = ['username', 'email', 'password', 'verification_code']
    missing_fields = validate_required_fields(data, required_fields)

    if missing_fields:
        log_operation(None, "add_user", "failed", f"Missing fields: {', '.join(missing_fields)}")
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    email = data.get('email')
    verification_code = data.get('verification_code')

    if not validate_verification_code(email, verification_code):
        log_operation(None, "add_user", "failed", f"Invalid or expired verification code for email: {email}")
        return jsonify({"success": False, "message": "Invalid or expired verification code"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log_operation(None, "add_user", "failed", f"Email already registered: {email}")
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_password = hash_password(data.get('password'))
    user = User(username=data.get('username'), email=email, password=hashed_password)

    db.session.add(user)
    try:
        db.session.commit()
        log_operation(user.id, "add_user", "success", f"User added successfully: {email}")
        return jsonify({"success": True, "message": "User added successfully", "user_id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        log_operation(None, "add_user", "failed", f"Database error: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


# 用户登录
@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    required_fields = ['email', 'password']
    missing_fields = validate_required_fields(data, required_fields)

    if missing_fields:
        log_operation(None, "login", "failed", f"Missing fields: {', '.join(missing_fields)}")
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password):
        log_operation(None, "login", "failed", f"Invalid credentials for email: {email}")
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    token = generate_jwt({"user_id": user.id})
    refresh_token = generate_refresh_token({"user_id": user.id})
    log_operation(user.id, "login", "success", f"Login successful for email: {email}")
    
    return jsonify({"success": True, "message": "Login successful", "token": token, "refresh_token": refresh_token}), 200


# 发送邮箱验证码
@user_bp.route('/api/send_verification_email', methods=['POST'])
def send_verification_email_route():
    data = request.json
    email = data.get('email')

    if not email:
        log_operation(None, "send_verification_email", "failed", "Email is required")
        return jsonify({"success": False, "message": "Email is required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        log_operation(None, "send_verification_email", "failed", f"Attempt to send verification code to registered email: {email}")
        return jsonify({"success": False, "message": "Email already registered"}), 400

    success = send_verification_email(email)
    if success:
        log_operation(None, "send_verification_email", "success", f"Verification email sent successfully to {email}")
        return jsonify({"success": True, "message": "Verification email sent successfully"}), 200

    log_operation(None, "send_verification_email", "failed", f"Failed to send verification email to {email}")
    return jsonify({"success": False, "message": "Failed to send email"}), 500


# 用户租赁信息展示
@user_bp.route('/api/user/rental_info', methods=['GET'])
def rental_info():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    rental_info = {
        "username": user.username,
        "email": user.email,
        "rental_expiry": user.rental_expiry,
        "total_traffic": sum(container.upload_traffic + container.download_traffic for container in user.containers),
        "server_list": [server.ip for server in user.servers],
    }
    return jsonify({"success": True, "rental_info": rental_info}), 200


# 用户历史记录接口
@user_bp.route('/api/user/history/<int:user_id>', methods=['GET'])
def user_history(user_id):
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


# 申请成为分销员
@user_bp.route('/api/user/apply_distributor', methods=['POST'])
def apply_distributor():
    """
    申请成为分销员接口
    请求参数：
        - user_id: 用户ID
    返回：
        - 成功或失败信息
    """
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        log_operation(None, "apply_distributor", "failed", "Missing user_id")
        return jsonify({"success": False, "message": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        log_operation(None, "apply_distributor", "failed", f"User not found: {user_id}")
        return jsonify({"success": False, "message": "User not found"}), 404

    if user.role == "distributor":
        log_operation(user.id, "apply_distributor", "failed", "User already a distributor")
        return jsonify({"success": False, "message": "User is already a distributor"}), 400

    try:
        user.role = "distributor"
        db.session.commit()
        log_operation(user.id, "apply_distributor", "success", f"User {user_id} approved as distributor")
        return jsonify({"success": True, "message": "User approved as distributor"}), 200
    except Exception as e:
        db.session.rollback()
        log_operation(user.id, "apply_distributor", "failed", f"Error approving distributor: {str(e)}")
        return jsonify({"success": False, "message": "Failed to apply as distributor"}), 500


# 下载 ACL 配置文件
@user_bp.route('/api/user/download_acl', methods=['GET'])
def download_acl():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    acl_filename = os.path.basename(f"{user_id}_acl.json")
    acl_file_path = os.path.join('acl_files', acl_filename)

    if not os.path.exists(acl_file_path):
        log_operation(user.id, "download_acl", "failed", f"ACL file not found for user: {user_id}")
        return jsonify({"success": False, "message": "ACL file not found"}), 404

    return send_from_directory(directory='acl_files', filename=acl_filename), 200
