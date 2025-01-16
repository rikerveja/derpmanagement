from flask import Blueprint, jsonify
from models import User, Server, Container, Rental, Alert, Traffic
from database import db
from datetime import datetime, timedelta

system_bp = Blueprint('system', __name__)

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
        return jsonify({
            'success': False,
            'message': f'Error getting system overview: {str(e)}'
        }), 500
