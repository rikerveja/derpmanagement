from flask import Blueprint, request, jsonify
from app.models import DockerContainer, DockerContainerTraffic, ServerTraffic, UserTraffic, Rental
from datetime import datetime
import requests
import logging
from app import db

# 定义蓝图
traffic_bp = Blueprint('traffic', __name__)

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
            return jsonify({
                "success": True,
                "container": {
                    "id": container.id,
                    "name": container.container_name
                },
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
                # 解析 eth0 设备的上传流量
                if 'eth0' in line:
                    metrics["upload_traffic"] = float(line.split(" ")[1])

            # 检查下载流量
            elif "node_network_receive_bytes_total" in line:
                # 解析 eth0 设备的下载流量
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

from flask import Blueprint, jsonify, request
from . import db  # 导入 db 实例
from datetime import datetime
from .models import Rental  # 导入 Rental 类，确保模型被导入

traffic_bp = Blueprint('traffic_bp', __name__)

@traffic_bp.route('/api/traffic/stats', methods=['POST'])
def get_traffic_stats():
    """
    按用户或服务器统计流量，并更新数据表
    """
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    try:
        # 按用户统计流量
        if user_id:
            # 从 docker_containers 表查询用户相关的容器流量
            user_traffic = DockerContainer.query.filter_by(user_id=user_id).limit(100).all()
            response_data = [
                {
                    "container_id": record.id,
                    "upload_traffic": round(record.upload_traffic / (1024 * 1024 * 1024), 2),  # 转换为GB
                    "download_traffic": round(record.download_traffic / (1024 * 1024 * 1024), 2),  # 转换为GB
                    "updated_at": record.updated_at.isoformat()  # 使用 updated_at 字段
                }
                for record in user_traffic
            ]

            # 更新用户流量统计
            total_traffic = sum((r.upload_traffic + r.download_traffic) / (1024 * 1024 * 1024) for r in user_traffic)  # 转换为GB
            traffic_limit = max(r.max_upload_traffic for r in user_traffic)  # 使用 max_upload_traffic

            # 更新或插入用户流量统计记录
            user_record = UserTraffic.query.filter_by(user_id=user_id).first()
            if user_record:
                user_record.upload_traffic = round(sum(r.upload_traffic for r in user_traffic) / (1024 * 1024 * 1024), 2)  # 转换为GB
                user_record.download_traffic = round(sum(r.download_traffic for r in user_traffic) / (1024 * 1024 * 1024), 2)  # 转换为GB
                user_record.total_traffic = round(total_traffic, 2)
                user_record.updated_at = datetime.utcnow()
            else:
                user_record = UserTraffic(
                    user_id=user_id,
                    upload_traffic=round(sum(r.upload_traffic for r in user_traffic) / (1024 * 1024 * 1024), 2),
                    download_traffic=round(sum(r.download_traffic for r in user_traffic) / (1024 * 1024 * 1024), 2),
                    total_traffic=round(total_traffic, 2),
                    updated_at=datetime.utcnow()
                )
                db.session.add(user_record)

            db.session.commit()

            # 更新租赁表的 traffic_usage
            rental_record = Rental.query.filter_by(user_id=user_id).first()  # 修改为 Rental
            if rental_record:
                rental_record.traffic_usage = round(total_traffic, 2)
                rental_record.updated_at = datetime.utcnow()
                db.session.commit()

            # 更新容器流量
            for record in user_traffic:
                container = DockerContainer.query.get(record.id)
                if container:
                    container.upload_traffic = round(record.upload_traffic / (1024 * 1024 * 1024), 2)  # 转换为GB
                    container.download_traffic = round(record.download_traffic / (1024 * 1024 * 1024), 2)  # 转换为GB
                    db.session.commit()

            return jsonify({"success": True, "user_traffic": response_data, "user_summary": {
                "total_traffic": round(total_traffic, 2),
                "traffic_limit": traffic_limit
            }}), 200

        # 按服务器统计流量
        if server_id:
            # 从 docker_containers 表查询服务器相关的容器流量
            server_traffic = DockerContainer.query.filter_by(server_id=server_id).limit(100).all()
            response_data = [
                {
                    "container_id": record.id,
                    "upload_traffic": round(record.upload_traffic / (1024 * 1024 * 1024), 2),  # 转换为GB
                    "download_traffic": round(record.download_traffic / (1024 * 1024 * 1024), 2),  # 转换为GB
                    "updated_at": record.updated_at.isoformat()  # 使用 updated_at 字段
                }
                for record in server_traffic
            ]

            # 更新服务器流量统计
            total_traffic = sum((r.upload_traffic + r.download_traffic) / (1024 * 1024 * 1024) for r in server_traffic)  # 转换为GB

            # 获取服务器的 remaining_traffic（从 servers 表中）
            server = Servers.query.get(server_id)
            remaining_traffic = round(server.remaining_traffic / (1024 * 1024 * 1024), 2) if server else 0  # 转换为GB

            # 获取 max_upload_traffic（流量限制）
            traffic_limit = max(r.max_upload_traffic for r in server_traffic)  # 使用 max_upload_traffic

            # 更新或插入服务器流量统计记录
            server_record = ServerTraffic.query.filter_by(server_id=server_id).first()
            if server_record:
                server_record.total_traffic = round(total_traffic, 2)
                server_record.remaining_traffic = remaining_traffic
                server_record.traffic_limit = traffic_limit
                server_record.traffic_used = round(total_traffic - remaining_traffic, 2)
                server_record.updated_at = datetime.utcnow()
            else:
                server_record = ServerTraffic(
                    server_id=server_id,
                    total_traffic=round(total_traffic, 2),
                    remaining_traffic=remaining_traffic,
                    traffic_limit=traffic_limit,
                    traffic_used=round(total_traffic - remaining_traffic, 2),
                    traffic_reset_date=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                db.session.add(server_record)

            db.session.commit()

            # 更新服务器的 remaining_traffic
            if server:
                server.remaining_traffic = remaining_traffic
                db.session.commit()

            # 更新容器流量
            for record in server_traffic:
                container = DockerContainer.query.get(record.id)
                if container:
                    container.upload_traffic = round(record.upload_traffic / (1024 * 1024 * 1024), 2)  # 转换为GB
                    container.download_traffic = round(record.download_traffic / (1024 * 1024 * 1024), 2)  # 转换为GB
                    db.session.commit()

            return jsonify({"success": True, "server_traffic": response_data, "server_summary": {
                "total_traffic": round(total_traffic, 2),
                "remaining_traffic": remaining_traffic,
                "traffic_limit": traffic_limit
            }}), 200

        return jsonify({"success": False, "message": "Missing user_id or server_id"}), 400

    except Exception as e:
        logging.error(f"Error fetching traffic stats: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching traffic stats: {str(e)}"}), 500



