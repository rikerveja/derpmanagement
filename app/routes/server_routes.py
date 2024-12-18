
from flask import Blueprint, request, jsonify
from app.models import Server

server_bp = Blueprint('server', __name__)

@server_bp.route('/api/add_server', methods=['POST'])
def add_server():
    data = request.json
    # Add server logic

@server_bp.route('/api/add_user_server', methods=['POST'])
def add_user_server():
    data = request.json
    # Add user-server logic
