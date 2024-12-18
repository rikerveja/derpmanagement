
from flask import Blueprint, request, jsonify
from app.models import UserContainer

container_bp = Blueprint('container', __name__)

@container_bp.route('/api/add_user_container', methods=['POST'])
def add_user_container():
    data = request.json
    # Add container logic

@container_bp.route('/api/remove_user_container', methods=['POST'])
def remove_user_container():
    data = request.json
    # Remove container logic
