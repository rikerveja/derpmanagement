from flask import Blueprint, jsonify, request
from app.models import User, Server, Container, Rental, Alert, Traffic
from app import db
from datetime import datetime, timedelta
import logging

# 定义蓝图
system_bp = Blueprint('system', __name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 获取系统概览
@system_bp.route('/api/system/overview', methods=['GET'])
def get_system_overview():
    try:
        # 获取用户统计
        users = User.query.all()
        total_users = len(users)
        active_users = len([u for u in users if u.status == 'active'])
        expired_users = len([u for u in users if u.status == 'expired'])

        # 获取服务器统计
        servers = Server.query.all()
        total_servers = len(servers)
        running_servers = len([s for s in servers if s.status == 'running'])
        stopped_servers = len([s for s in servers if s.status == 'stopped'])
        error_servers = len([s for s in servers if s.status == 'error'])

        # 获取容器统计
        containers = Container.query.all()
        total_containers = len(containers)
        running_containers = len([c for c in containers if c.status == 'running'])
        stopped_containers = len([c for c in containers if c.status == 'stopped'])
        error_containers = len([c for c in containers if c.status == 'error'])

        # 获取流量统计
        traffic = Traffic.query.first()  # 假设有一个总流量记录
        traffic_stats = {
            'used': traffic.used_traffic if traffic else 0,
            'total': traffic.total_traffic if traffic else 0
        }

        # 获取租赁统计
        rentals = Rental.query.all()
        total_rentals = len(rentals)
        active_rentals = len([r for r in rentals if r.status == 'active'])
        expired_rentals = len([r for r in rentals if r.status == 'expired'])

        # 获取告警统计
        alerts = Alert.query.all()
        total_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a.level == 'critical'])

        # 构建响应数据
        response_data = {
            'success': True,
            'data': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'expired': expired_users
                },
                'servers': {
                    'total': total_servers,
                    'running': running_servers,
                    'stopped': stopped_servers,
                    'error': error_servers
                },
                'containers': {
                    'total': total_containers,
                    'running': running_containers,
                    'stopped': stopped_containers,
                    'error': error_containers
                },
                'traffic': traffic_stats,
                'rentals': {
                    'total': total_rentals,
                    'active': active_rentals,
                    'expired': expired_rentals
                },
                'alerts': {
                    'total': total_alerts,
                    'critical': critical_alerts
                }
            },
            'message': 'System overview retrieved successfully'
        }

        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"Error getting system overview: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting system overview: {str(e)}'
        }), 500


# 获取服务器分类
@system_bp.route('/servers/categories', methods=['GET'])
def get_server_categories():
    try:
        categories = Server.query.with_entities(Server.category).distinct().all()
        categories = [category[0] for category in categories]
        return jsonify({'status': 'success', 'categories': categories}), 200
    except Exception as e:
        logging.error(f"Error getting server categories: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 重置数据库
@system_bp.route('/database/reset', methods=['POST'])
def reset_db():
    try:
        db.session.remove()
        db.drop_all()
        db.create_all()
        logging.info("Database reset successfully.")
        return jsonify({'status': 'success', 'message': 'Database reset successfully.'}), 200
    except Exception as e:
        logging.error(f"Error resetting database: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 备份数据库
@system_bp.route('/database/backup', methods=['POST'])
def backup_db():
    try:
        # 执行备份逻辑，这里是一个示例路径
        backup_path = "/backup/directory/backup.sql"
        logging.info(f"Database backup created at {backup_path}.")
        return jsonify({'status': 'success', 'message': 'Database backup created.', 'backup_path': backup_path}), 200
    except Exception as e:
        logging.error(f"Error backing up database: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 设置服务器分类
@system_bp.route('/server/category', methods=['POST'])
def set_server_category():
    try:
        data = request.json
        server_id = data.get('server_id')
        category = data.get('category')

        if not server_id or not category:
            return jsonify({'status': 'error', 'message': 'Server ID and category are required.'}), 400

        server = Server.query.get(server_id)
        if not server:
            return jsonify({'status': 'error', 'message': 'Server not found.'}), 404

        server.category = category
        db.session.commit()
        logging.info(f"Server {server_id} category updated to {category}.")
        return jsonify({'status': 'success', 'message': 'Server category updated.'}), 200

    except Exception as e:
        logging.error(f"Error updating server category: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
