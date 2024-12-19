from flask import Blueprint, request, jsonify
from app.models import SerialNumber, User
from app import db

rental_bp = Blueprint('rental', __name__)

@rental_bp.route('/status', methods=['GET'])
def rental_status():
    """
    查看租赁状态
    """
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    serial_numbers = [
        {
            "serial_number": sn.code,
            "status": sn.status,
            "duration_days": sn.duration_days,
            "used_at": sn.used_at,
            "created_at": sn.created_at,
        }
        for sn in user.serial_numbers
    ]
    return jsonify({"success": True, "serial_numbers": serial_numbers}), 200

@rental_bp.route('/renew', methods=['POST'])
def renew_rental():
    """
    续费租赁
    """
    data = request.json
    user_id = data.get('user_id')
    serial_code = data.get('serial_code')

    serial_number = SerialNumber.query.filter_by(code=serial_code, user_id=user_id).first()
    if not serial_number:
        return jsonify({"success": False, "message": "Serial number not found"}), 404

    serial_number.status = 'active'
    db.session.commit()
    return jsonify({"success": True, "message": "Rental renewed successfully"}), 200
