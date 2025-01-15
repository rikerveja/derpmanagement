from flask import Blueprint, request, jsonify
from app.models import UserContainer, DockerContainerTraffic, ServerTraffic, UserTraffic, Rentals
from datetime import datetime
import requests
import logging

# 定义蓝图
traffic_bp = Blueprint('traffic', __name__)

# 实时流量监控（所有容器）
@traffic_bp.route('/api/traffic/realtime', methods=['GET'])
def realtime_traffic():
    """
    获取所有容器的实时流量监控
    """
    try:
        traffic_data = []
        containers = UserContainer.query.all()
        
        for container in containers:
            metrics_url = f"http://{container.server_ip}:{container.metrics_port}/metrics"
            metrics = fetch_traffic_metrics(metrics_url)
            
            if metrics:
                traffic_data.append({
                    "container_id": container.id,
                    "server_id": container.server_id,
                    "upload_traffic": metrics.get("upload_traffic"),
                    "download_traffic": metrics.get("download_traffic"),
                    "timestamp": datetime.utcnow().isoformat()
                })

        return jsonify({"success": True, "traffic_data": traffic_data}), 200
    except Exception as e:
        logging.error(f"Error fetching realtime traffic data: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching realtime traffic: {str(e)}"}), 500

# 实时流量监控（单个容器）
@traffic_bp.route('/api/traffic/realtime/<int:container_id>', methods=['GET'])
def get_realtime_traffic(container_id):
    """
    获取容器的实时流量数据
    """
    try:
        container = UserContainer.query.get(container_id)
        if not container:
            return jsonify({"success": False, "message": "Container not found"}), 404

        metrics_url = f"http://{container.server_ip}:{container.metrics_port}/metrics"
        metrics = fetch_traffic_metrics(metrics_url)

        if metrics:
            return jsonify({
                "success": True,
                "traffic": {
                    "upload_traffic": metrics.get("upload_traffic"),
                    "download_traffic": metrics.get("download_traffic")
                },
                "timestamp": datetime.utcnow().isoformat()
            }), 200

        return jsonify({"success": False, "message": "Failed to fetch metrics"}), 500
    except Exception as e:
        logging.error(f"Error fetching realtime traffic for container {container_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching realtime traffic: {str(e)}"}), 500

# 用户流量历史统计
@traffic_bp.route('/api/traffic/history/<int:user_id>', methods=['GET'])
def traffic_history(user_id):
    """
    获取用户的流量历史统计
    """
    try:
        history_data = DockerContainerTraffic.query.filter_by(user_id=user_id).limit(100).all()
        
        response_data = [
            {
                "container_id": record.container_id,
                "upload_traffic": record.upload_traffic,
                "download_traffic": record.download_traffic,
                "remaining_traffic": record.remaining_traffic,
                "timestamp": record.timestamp.isoformat()
            }
            for record in history_data
        ]

        return jsonify({"success": True, "user_id": user_id, "history_data": response_data}), 200
    except Exception as e:
        logging.error(f"Error fetching traffic history for user {user_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching traffic history: {str(e)}"}), 500

# 按用户或服务器统计流量
@traffic_bp.route('/api/traffic/stats', methods=['POST'])
def get_traffic_stats():
    """
    按用户或服务器统计流量
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    try:
        if user_id:
            user_traffic = DockerContainerTraffic.query.filter_by(user_id=user_id).limit(100).all()
            response_data = [
                {
                    "container_id": record.container_id,
                    "upload_traffic": record.upload_traffic,
                    "download_traffic": record.download_traffic,
                    "remaining_traffic": record.remaining_traffic,
                    "timestamp": record.timestamp.isoformat()
                }
                for record in user_traffic
            ]

            # 更新用户流量统计
            total_traffic = sum(r.upload_traffic + r.download_traffic for r in user_traffic)
            remaining_traffic = sum(r.remaining_traffic for r in user_traffic)
            traffic_limit = max(r.traffic_limit for r in user_traffic)

            user_record = UserTraffic.query.filter_by(user_id=user_id).first()
            if user_record:
                user_record.upload_traffic = sum(r.upload_traffic for r in user_traffic)
                user_record.download_traffic = sum(r.download_traffic for r in user_traffic)
                user_record.total_traffic = total_traffic
                user_record.remaining_traffic = remaining_traffic
                user_record.traffic_limit = traffic_limit
                user_record.updated_at = datetime.utcnow()
            else:
                user_record = UserTraffic(
                    user_id=user_id,
                    upload_traffic=sum(r.upload_traffic for r in user_traffic),
                    download_traffic=sum(r.download_traffic for r in user_traffic),
                    total_traffic=total_traffic,
                    remaining_traffic=remaining_traffic,
                    traffic_limit=traffic_limit,
                    updated_at=datetime.utcnow()
                )

            UserTraffic.query.session.add(user_record)
            UserTraffic.query.session.commit()

            # 更新租赁表的 traffic_usage
            rental_record = Rentals.query.filter_by(user_id=user_id).first()
            if rental_record:
                rental_record.traffic_usage = total_traffic
                rental_record.updated_at = datetime.utcnow()
                Rentals.query.session.commit()

            return jsonify({"success": True, "user_traffic": response_data, "user_summary": {
                "total_traffic": total_traffic,
                "remaining_traffic": remaining_traffic,
                "traffic_limit": traffic_limit
            }}), 200

        if server_id:
            server_traffic = DockerContainerTraffic.query.filter_by(server_id=server_id).limit(100).all()
            response_data = [
                {
                    "container_id": record.container_id,
                    "upload_traffic": record.upload_traffic,
                    "download_traffic": record.download_traffic,
                    "remaining_traffic": record.remaining_traffic,
                    "timestamp": record.timestamp.isoformat()
                }
                for record in server_traffic
            ]

            # 更新服务器流量统计
            total_traffic = sum(r.upload_traffic + r.download_traffic for r in server_traffic)
            remaining_traffic = sum(r.remaining_traffic for r in server_traffic)
            traffic_limit = max(r.traffic_limit for r in server_traffic)

            server_record = ServerTraffic.query.filter_by(server_id=server_id).first()
            if server_record:
                server_record.total_traffic = total_traffic
                server_record.remaining_traffic = remaining_traffic
                server_record.traffic_limit = traffic_limit
                server_record.traffic_used = total_traffic - remaining_traffic
                server_record.updated_at = datetime.utcnow()
            else:
                server_record = ServerTraffic(
                    server_id=server_id,
                    total_traffic=total_traffic,
                    remaining_traffic=remaining_traffic,
                    traffic_limit=traffic_limit,
                    traffic_used=total_traffic - remaining_traffic,
                    traffic_reset_date=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )

            ServerTraffic.query.session.add(server_record)
            ServerTraffic.query.session.commit()

            return jsonify({"success": True, "server_traffic": response_data, "server_summary": {
                "total_traffic": total_traffic,
                "remaining_traffic": remaining_traffic,
                "traffic_limit": traffic_limit
            }}), 200

        return jsonify({"success": False, "message": "Missing user_id or server_id"}), 400
    except Exception as e:
        logging.error(f"Error fetching traffic stats: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching traffic stats: {str(e)}"}), 500

# 超流量检测
@traffic_bp.route('/api/traffic/overlimit', methods=['GET'])
def detect_overlimit_users():
    """
    检测超流量用户
    """
    try:
        overlimit_users = DockerContainerTraffic.query.filter(DockerContainerTraffic.remaining_traffic < 0).limit(100).all()
        response_data = [
            {
                "container_id": record.container_id,
                "total_traffic": record.upload_traffic + record.download_traffic,
                "remaining_traffic": record.remaining_traffic
            }
            for record in overlimit_users
        ]

        return jsonify({"success": True, "overlimit_users": response_data}), 200
    except Exception as e:
        logging.error(f"Error detecting overlimit users: {str(e)}")
        return jsonify({"success": False, "message": f"Error detecting overlimit users: {str(e)}"}), 500

# 从 metrics 提取流量数据
def fetch_traffic_metrics(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        metrics = {}

        for line in response.text.splitlines():
            if "node_network_receive_bytes_total" in line:
                metrics["download_traffic"] = int(float(line.split(" ")[1]))
            elif "node_network_transmit_bytes_total" in line:
                metrics["upload_traffic"] = int(float(line.split(" ")[1]))

        return metrics
    except Exception as e:
        logging.error(f"Error fetching metrics from {url}: {str(e)}")
        return None
