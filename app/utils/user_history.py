from flask import Blueprint, request, jsonify
from app.models import UserHistory
from app import db
import logging

# 定义蓝图
user_history_bp = Blueprint('user_history', __name__)

# 更新用户历史记录
@user_history_bp.route('/api/rental/history/update/<int:id>', methods=['PUT'])
def update_user_history(id):
    """
    更新用户的历史记录
    :param id: 用户历史记录的 ID
    """
    data = request.json
    total_traffic = data.get('total_traffic')
    rental_end = data.get('rental_end')

    # 查找历史记录
    history = UserHistory.query.get(id)
    if not history:
        logging.warning(f"User history not found for ID {id}")
        return jsonify({"success": False, "message": "User history not found"}), 404

    try:
        # 更新字段，如果请求数据中有提供新的值，则更新，否则保留原值
        history.total_traffic = total_traffic if total_traffic else history.total_traffic
        history.rental_end = rental_end if rental_end else history.rental_end
        
        # 提交更改
        db.session.commit()
        
        logging.info(f"User history updated successfully for ID {id}")
        return jsonify({"success": True, "message": "User history updated successfully"}), 200
    except Exception as e:
        # 出现错误时回滚数据库事务
        db.session.rollback()
        logging.error(f"Error updating user history for ID {id}: {e}")
        return jsonify({"success": False, "message": f"Error updating user history: {str(e)}"}), 500

# 删除用户历史记录
@user_history_bp.route('/api/rental/history/delete/<int:id>', methods=['DELETE'])
def delete_user_history(id):
    """
    删除指定用户的历史记录
    :param id: 用户历史记录的 ID
    """
    # 查找用户历史记录
    history = UserHistory.query.get(id)
    if not history:
        logging.warning(f"User history not found for ID {id}")
        return jsonify({"success": False, "message": "User history not found"}), 404

    try:
        # 删除历史记录
        db.session.delete(history)
        db.session.commit()
        
        logging.info(f"User history deleted successfully for ID {id}")
        return jsonify({"success": True, "message": "User history deleted successfully"}), 200
    except Exception as e:
        # 出现错误时回滚数据库事务
        db.session.rollback()
        logging.error(f"Error deleting user history for ID {id}: {e}")
        return jsonify({"success": False, "message": f"Error deleting user history: {str(e)}"}), 500
