from flask import Blueprint, request, jsonify
from app import db
from app.models import DockerContainer, DockerContainerTraffic, ServerTraffic, ServerTrafficMonitoring, UserTraffic, Rentals
from datetime import datetime, timedelta
import requests
import logging

# 定义蓝图
traffic_bp = Blueprint('traffic', __name__)

# 字节转GB并保留2位小数
def bytes_to_gb(byte_value):
    """
    将字节转换为GB，并保留两位小数
    :param byte_value: 字节数
    :return: 转换后的GB数
    """
    if byte_value is None:
        return 0.00
    gb_value = byte_value / (1024 ** 3)
    return round(gb_value, 2)

# 获取下个月1日的日期
def get_next_month_first_day():
    today = datetime.utcnow()
    next_month = today.replace(day=28) + timedelta(days=4)  # 通过28号加4天来跳到下个月
    return next_month.replace(day=1)

# 保存流量数据接口
@traffic_bp.route('/api/traffic/save_traffic', methods=['POST'])
def save_traffic():
    """
    保存流量数据到多个数据表
    :param container_id: 容器ID
    :param upload_traffic: 上传流量
    :param download_traffic: 下载流量
    :param traffic_limit: 流量限制
    :param remaining_traffic: 剩余流量
    """
    try:
        # 获取请求的数据
        data = request.get_json()
        container_id = data.get('container_id')
        upload_traffic = data.get('upload_traffic')  # 上传流量（字节）
        download_traffic = data.get('download_traffic')  # 下载流量（字节）
        remaining_traffic = data.get('remaining_traffic', 0)  # 剩余流量，默认为0

        if not container_id or upload_traffic is None or download_traffic is None:
            return jsonify({'error': 'Missing container_id, upload_traffic or download_traffic'}), 400

        # 查询容器的流量限制，获取 `max_upload_traffic`
        container = DockerContainer.query.filter_by(container_id=container_id).first()
        if not container:
            return jsonify({'error': 'Container not found'}), 404

        max_upload_traffic = container.max_upload_traffic  # 获取容器流量限制

        # 转换字节为GB
        upload_traffic_gb = bytes_to_gb(upload_traffic)
        download_traffic_gb = bytes_to_gb(download_traffic)

        # 获取当前时间戳
        timestamp = datetime.utcnow()
        next_month_first_day = get_next_month_first_day()

        # 1. 保存容器流量数据到 `DockerContainerTraffic`
        traffic_entry = DockerContainerTraffic(
            container_id=container_id,
            upload_traffic=upload_traffic_gb,
            download_traffic=download_traffic_gb,
            traffic_limit=max_upload_traffic,  # 使用容器的流量限制
            remaining_traffic=remaining_traffic,
            timestamp=timestamp,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(traffic_entry)

        # 2. 更新服务器流量监控数据到 `ServerTrafficMonitoring`
        server_id = container.server_id
        server_traffic_monitoring_entry = ServerTrafficMonitoring(
            server_id=server_id,
            total_traffic=upload_traffic + download_traffic,  # 总流量（字节）
            used_traffic=upload_traffic + download_traffic,
            remaining_traffic=remaining_traffic,
            timestamp=timestamp
        )
        db.session.add(server_traffic_monitoring_entry)

        # 3. 更新 `ServerTraffic` 表
        server_traffic = ServerTraffic.query.filter_by(server_id=server_id).first()
        if server_traffic:
            # 计算服务器流量限制和剩余流量
            total_server_limit = sum([container.max_upload_traffic for container in DockerContainer.query.filter_by(server_id=server_id).all()])
            total_server_remaining = sum([container.remaining_traffic for container in DockerContainer.query.filter_by(server_id=server_id).all()])

            # 只有当是每月1日第一次保存流量数据时，才重置流量
            if server_traffic.traffic_reset_date != next_month_first_day:
                # 只有在每月1日才会重置流量
                server_traffic.remaining_traffic = total_server_limit  # 重置为服务器流量限制
                server_traffic.total_traffic = total_server_limit  # 总流量重置为流量限制
                server_traffic.traffic_used = 0  # 已用流量清零
                server_traffic.traffic_reset_date = next_month_first_day  # 设置为下个月1日
            else:
                # 否则，更新剩余流量
                server_traffic.remaining_traffic = total_server_remaining
            server_traffic.updated_at = datetime.utcnow()
        else:
            total_server_limit = sum([container.max_upload_traffic for container in DockerContainer.query.filter_by(server_id=server_id).all()])
            server_traffic = ServerTraffic(
                server_id=server_id,
                total_traffic=total_server_limit,
                remaining_traffic=remaining_traffic,
                traffic_limit=total_server_limit,
                traffic_used=upload_traffic + download_traffic,
                traffic_reset_date=next_month_first_day,
                updated_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(server_traffic)

        # 4. 更新 `UserTraffic` 表
        user_id = container.user_id
        user_traffic = UserTraffic.query.filter_by(user_id=user_id).first()
        if user_traffic:
            user_traffic.upload_traffic += upload_traffic_gb
            user_traffic.download_traffic += download_traffic_gb
            user_traffic.total_traffic += (upload_traffic_gb + download_traffic_gb)
            user_traffic.remaining_traffic = remaining_traffic
            user_traffic.updated_at = datetime.utcnow()
        else:
            user_traffic = UserTraffic(
                user_id=user_id,
                upload_traffic=upload_traffic_gb,
                download_traffic=download_traffic_gb,
                total_traffic=(upload_traffic_gb + download_traffic_gb),
                remaining_traffic=remaining_traffic,
                updated_at=datetime.utcnow()
            )
            db.session.add(user_traffic)

        # 5. 更新 `docker_containers` 表
        if container:
            # 根据POST参数来更新指定的字段
            if upload_traffic is not None:
                container.upload_traffic = upload_traffic_gb  # 精准更新上传流量
            if download_traffic is not None:
                container.download_traffic = download_traffic_gb  # 精准更新下载流量

            db.session.commit()

        # 6. 更新 `servers` 表中的剩余流量
        server = Server.query.filter_by(server_id=server_id).first()
        if server:
            if remaining_traffic is not None:
                server.remaining_traffic = remaining_traffic  # 精准更新剩余流量

            db.session.commit()

        db.session.commit()

        return jsonify({'message': 'Traffic data saved successfully'}), 200

    except Exception as e:
        logging.error(f"Error saving traffic data: {str(e)}")
        db.session.rollback()  # 回滚事务
        return jsonify({'error': 'Internal server error'}), 500


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

            # 计算用户流量统计
            total_traffic = sum(r.upload_traffic + r.download_traffic for r in user_traffic)
            remaining_traffic = sum(r.remaining_traffic for r in user_traffic)
            traffic_limit = max(r.traffic_limit for r in user_traffic)

            # 仅读取用户流量数据，不进行数据库写入
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

            # 计算服务器流量统计
            total_traffic = sum(r.upload_traffic + r.download_traffic for r in server_traffic)
            remaining_traffic = sum(r.remaining_traffic for r in server_traffic)
            traffic_limit = max(r.traffic_limit for r in server_traffic)

            # 仅读取服务器流量数据，不进行数据库写入
            return jsonify({"success": True, "server_traffic": response_data, "server_summary": {
                "total_traffic": total_traffic,
                "remaining_traffic": remaining_traffic,
                "traffic_limit": traffic_limit
            }}), 200

        return jsonify({"success": False, "message": "Missing user_id or server_id"}), 400
    except Exception as e:
        logging.error(f"Error fetching traffic stats: {str(e)}")
        return jsonify({"success": False, "message": f"Error fetching traffic stats: {str(e)}"}), 500
