
from flask import Blueprint, request, jsonify
from app.models import User
from app.utils.auth import hash_password, check_password, generate_jwt
from app.utils.email_utils import send_verification_email, validate_verification_code

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    # Add user logic

@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # Login logic

@user_bp.route('/api/send_verification_email', methods=['POST'])
def send_verification_email_route():
    data = request.json
    # Send verification email logic
