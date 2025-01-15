from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
import os
import subprocess
from app import db  # 假设 Flask-SQLAlchemy 设置

# 创建 Blueprint
system_bp = Blueprint('system', __name__)

# 假设你有一个数据库操作模块（可以是一个单独的类或函数）
from app.database import reset_database, backup_database

# 假设你有一个服务器分类的字典或者数据库模型
from app.models import Server

# 路由：获取服务器分类
@system_bp.route('/servers/categories', methods=['GET'])
def get_server_categories():
    try:
        # 假设Server模型有category字段，获取所有不同类别的服务器
        categories = Server.query.with_entities(Server.category).distinct().all()
        categories = [category[0] for category in categories]
        return jsonify({'status': 'success', 'categories': categories}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 路由：重置数据库
@system_bp.route('/database/reset', methods=['POST'])
def reset_db():
    try:
        # 调用数据库重置函数
        reset_database()
        return jsonify({'status': 'success', 'message': 'Database reset successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 路由：备份数据库
@system_bp.route('/database/backup', methods=['POST'])
def backup_db():
    try:
        # 调用数据库备份函数
        backup_path = backup_database()
        return jsonify({'status': 'success', 'message': 'Database backup created.', 'backup_path': backup_path}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 路由：服务器分类（假设是通过数据库操作）
@system_bp.route('/server/category', methods=['POST'])
def set_server_category():
    try:
        data = request.json
        server_id = data.get('server_id')
        category = data.get('category')

        if not server_id or not category:
            raise BadRequest('Server ID and category are required.')

        # 更新服务器的分类（假设数据库中有此字段）
        server = Server.query.get(server_id)
        if not server:
            raise BadRequest('Server not found.')

        server.category = category
        server.save()  # 保存更新

        return jsonify({'status': 'success', 'message': 'Server category updated.'}), 200
    except BadRequest as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 假设 reset_database 和 backup_database 分别是定义的数据库操作函数
def reset_database():
    # 实际的数据库重置逻辑
    # 示例：删除所有表并重新创建
    db.session.remove()
    db.drop_all()
    db.create_all()

def backup_database():
    # 使用 mysqldump 进行数据库备份的例子
    backup_dir = '/backup/directory'
    filename = f"{backup_dir}/backup_{int(time.time())}.sql"
    
    # 使用 subprocess 执行系统命令备份数据库
    command = f"mysqldump -u root -p your_database_name > {filename}"
    subprocess.run(command, shell=True, check=True)
    
    return filename
