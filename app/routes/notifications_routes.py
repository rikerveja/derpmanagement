from flask import Blueprint, jsonify

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/renewal_reminder', methods=['GET'])
def renewal_reminder():
    """
    ģ����������
    """
    # ʾ����������������
    return jsonify({"success": True, "message": "Renewal reminder sent"}), 200
