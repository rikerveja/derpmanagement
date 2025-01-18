from flask import Blueprint, request, jsonify
from app.models import DockerContainer, DockerContainerTraffic, ServerTraffic, UserTraffic, Rental
from datetime import datetime
import requests
import logging

# 定义蓝图
traffic_bp = Blueprint('traffic', __name__)

# 将字节转换为 GB
def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024 ** 3), 2)  # 1GB = 1024^3 字节

# 从容器名称提取 IP 地址
def extract_ip_from_container_name(container_name):
    """
    从容器名称中提取 IP 地址，假设容器名称格式为 "120_79_137_248_derper_4"
    """
    parts = container_name.split('_')
    if len(parts) >= 4:  # 确保容器名称包含 IP 地址
        return '.'.join(parts[:4])  # 提取前三个部分并将它们连接成 IP 地址
    return None  # 如果容器名称格式不正确，返回 None

# 实时流量监控（所有容器）
@traffic_bp.route('/api/traffic/realtime', methods=['GET'])
def realtime_traffic():
    """
    获取所有容器的实时流量监控
    """
    try:
        traffic_data = []
        containers = DockerContainer.query.all()  # 获取所有 Docker 容器
        
        for container in containers:
            # 从 DockerContainer 中提取 container_name
            server_ip = extract_ip_from_container_name(container.container_name)
            if not server_ip:
                continue  # 如果无法从容器名称中提取 IP 地址，跳过此容器

            # 使用 node_exporter_port 获取流量数据
            metrics_url = f"http://{server_ip}:{container.node_exporter_port}/metrics"
            metrics = fetch_traffic_metrics(metrics_url)

            if metrics:
                # 转换流量为 GB 单位
                upload_traffic_gb = bytes_to_gb(metrics.get("upload_traffic"))
                download_traffic_gb = bytes_to_gb(metrics.get("download_traffic"))

                # 更新数据库中的流量
                container.upload_traffic = upload_traffic_gb
                container.download_traffic = download_traffic_gb
                db.session.commit()  # 提交更新

                traffic_data.append({
                    "container_id": container.id,
                    "server_id": container.server_id,
                    "upload_traffic": upload_traffic_gb,
                    "download_traffic": download_traffic_gb,
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
        container = DockerContainer.query.get(container_id)  # 从 DockerContainer 获取容器
        if not container:
            return jsonify({"success": False, "message": "Container not found"}), 404

        # 从 DockerContainer 中提取 container_name
        server_ip = extract_ip_from_container_name(container.container_name)
        if not server_ip:
            return jsonify({"success": False, "message": "Invalid container name format, unable to extract IP"}), 400

        # 使用 node_exporter_port 获取流量数据
        metrics_url = f"http://{server_ip}:{container.node_exporter_port}/metrics"
        metrics = fetch_traffic_metrics(metrics_url)

        if metrics:
            # 转换流量为 GB 单位
            upload_traffic_gb = bytes_to_gb(metrics.get("upload_traffic"))
            download_traffic_gb = bytes_to_gb(metrics.get("download_traffic"))

            return jsonify({
                "success": True,
                "container": {
                    "id": container.id,
                    "name": container.container_name
                },
                "traffic": {
                    "upload_traffic": upload_traffic_gb,
                    "download_traffic": download_traffic_gb
                },
                "timestamp": datetime.utcnow().isoformat()
            }), 200

        return jsonify({"success": False, "message": "Failed to fetch metrics"}), 500
    except Exception as e:
        logging.error(f"Error fetching realtime traffic for container {container_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching realtime traffic: {str(e)}"}), 500

# 从 metrics 提取流量数据
def fetch_traffic_metrics(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        metrics = {}

        # 处理返回的多行文本数据
        for line in response.text.splitlines():
            # 检查上传流量
            if "node_network_transmit_bytes_total" in line:
                if 'eth0' in line:
                    metrics["upload_traffic"] = float(line.split(" ")[1])

            # 检查下载流量
            elif "node_network_receive_bytes_total" in line:
                if 'eth0' in line:
                    metrics["download_traffic"] = float(line.split(" ")[1])

        # 如果找到了上传和下载流量，就返回 metrics
        if "upload_traffic" in metrics and "download_traffic" in metrics:
            return metrics
        else:
            logging.error("Could not extract traffic data from metrics.")
            return None

    except Exception as e:
        logging.error(f"Error fetching metrics from {url}: {str(e)}")
        return None

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
                "upload_traffic": bytes_to_gb(record.upload_traffic),
                "download_traffic": bytes_to_gb(record.download_traffic),
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
                    "upload_traffic": bytes_to_gb(record.upload_traffic),
                    "download_traffic": bytes_to_gb(record.download_traffic),
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
                    "upload_traffic": bytes_to_gb(record.upload_traffic),
                    "download_traffic": bytes_to_gb(record.download_traffic),
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
