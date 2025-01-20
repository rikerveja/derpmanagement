from flask import Blueprint, jsonify, request
import requests  # 正确导入 requests 库
from app import db
from app.models import Server, DockerContainer, DockerContainerTraffic, ServerTraffic, ServerTrafficMonitoring, UserTraffic, Rental
from datetime import datetime, timedelta
import logging
from decimal import Decimal

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
        return Decimal(0.00)
    gb_value = Decimal(byte_value) / (1024 ** 3)  # 转换为GB
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
        remaining_traffic = data.get('remaining_traffic', 0)  # 剩余流量，默认为0（字节）

        if not container_id or upload_traffic is None or download_traffic is None:
            return jsonify({'error': 'Missing container_id, upload_traffic or download_traffic'}), 400

        # 查询容器的流量限制，获取 `max_upload_traffic`
        container = DockerContainer.query.filter_by(container_id=container_id).first()
        if not container:
            logging.error(f"Container with ID {container_id} not found.")
            return jsonify({'error': 'Container not found'}), 404

        max_upload_traffic = Decimal(container.max_upload_traffic)  # 获取容器流量限制
        logging.debug(f"Container {container_id} max upload traffic: {max_upload_traffic}")

        # 转换字节为GB
        upload_traffic_gb = bytes_to_gb(upload_traffic)  # 字节转GB
        download_traffic_gb = bytes_to_gb(download_traffic)  # 字节转GB
        remaining_traffic_gb = bytes_to_gb(remaining_traffic)  # 字节转GB
        logging.debug(f"Converted upload traffic: {upload_traffic_gb} GB, download traffic: {download_traffic_gb} GB")

        # 获取当前时间戳
        timestamp = datetime.utcnow()
        next_month_first_day = get_next_month_first_day()
        logging.debug(f"Next month's first day: {next_month_first_day}")

        # 1. 获取 docker_containers 中的 id（自增主键）
        container_id_db = container.id  # 这里获取到的是自增的 id，而不是原始的 container_id

        # 2. 保存容器流量数据到 `DockerContainerTraffic`
        traffic_entry = DockerContainerTraffic(
            container_id=container_id_db,  # 存储的是自增的 id
            upload_traffic=upload_traffic_gb,  # GB单位
            download_traffic=download_traffic_gb,  # GB单位
            traffic_limit=max_upload_traffic,  # 使用容器的流量限制
            remaining_traffic=remaining_traffic_gb,  # GB单位
            timestamp=timestamp,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(traffic_entry)

# 3. 更新服务器流量数据到 `ServerTraffic` 表，并记录流量监控快照
server_id = container.server_id  # 获取 server_id
timestamp = datetime.utcnow()  # 获取当前时间戳

# 计算所有容器的总流量
total_server_limit = sum([Decimal(container.max_upload_traffic) for container in DockerContainer.query.filter_by(server_id=server_id).all()])
total_server_used = sum([Decimal(c.upload_traffic) for c in DockerContainer.query.filter_by(server_id=server_id).all()])

# 确保所有的计算结果都是 Decimal 类型
total_server_remaining = total_server_limit - total_server_used  # 总流量使用后剩余流量

# 创建流量监控快照，记录当前时间戳
server_traffic_monitoring_entry = ServerTrafficMonitoring(
    server_id=server_id,
    total_traffic=total_server_limit,  # 使用GB单位
    used_traffic=total_server_used,  # 使用GB单位
    remaining_traffic=total_server_remaining,  # 使用GB单位
    timestamp=timestamp
)
db.session.add(server_traffic_monitoring_entry)

# 更新 `ServerTraffic` 表（累加所有容器的流量）
server_traffic = ServerTraffic.query.filter_by(id=server_id).first()  # 根据自增的 id 查询

if server_traffic:
    # 只有当是每月1日第一次保存流量数据时，才重置流量
    if server_traffic.traffic_reset_date != get_next_month_first_day():
        # 重置流量
        server_traffic.remaining_traffic = total_server_remaining  # 重置为服务器流量限制
        server_traffic.total_traffic = total_server_limit  # 总流量重置为流量限制
        server_traffic.traffic_used = total_server_used  # 已用流量
        server_traffic.traffic_reset_date = get_next_month_first_day()  # 设置为下个月1日
        logging.debug(f"Reset server traffic for server {server_id}")
    else:
        # 否则，更新剩余流量
        server_traffic.remaining_traffic = total_server_remaining
        server_traffic.traffic_used = total_server_used
        logging.debug(f"Updated remaining traffic for server {server_id}")

    server_traffic.updated_at = timestamp  # 更新时间戳
else:
    # 如果没有找到服务器流量记录，则创建新记录
    server_traffic = ServerTraffic(
        id=server_id,  # 修改了这里的id为自增的主键
        total_traffic=total_server_limit,  # 使用GB单位
        remaining_traffic=total_server_remaining,  # 使用GB单位
        traffic_limit=total_server_limit,
        traffic_used=total_server_used,  # 使用GB单位
        traffic_reset_date=get_next_month_first_day(),  # 设置为下个月1日
        updated_at=timestamp,
        created_at=timestamp
    )
    db.session.add(server_traffic)

# 提交所有更改到数据库
db.session.commit()

        # 4. 更新 `UserTraffic` 表 
        user_id = container.user_id
        user_traffic = UserTraffic.query.filter_by(user_id=user_id).first()

        if user_traffic:

            # 显式将 Decimal 转换为 Decimal 再进行操作
            user_traffic.upload_traffic += upload_traffic_gb  # 使用GB单位
            user_traffic.download_traffic += download_traffic_gb  # 使用GB单位
            user_traffic.total_traffic += upload_traffic_gb + download_traffic_gb  # 使用GB单位
            user_traffic.remaining_traffic = remaining_traffic_gb  # 使用GB单位

            user_traffic.updated_at = datetime.utcnow()
        else:
            # 显式将 Decimal 转换为 Decimal

            user_traffic = UserTraffic(
                user_id=user_id,
                upload_traffic=upload_traffic_gb,  # 使用GB单位
                download_traffic=download_traffic_gb,  # 使用GB单位
                total_traffic=upload_traffic_gb + download_traffic_gb,  # 使用GB单位
                remaining_traffic=remaining_traffic_gb,  # 使用GB单位
                updated_at=datetime.utcnow()
            )
            db.session.add(user_traffic)

        # 6. 更新 `docker_containers` 表
        if container:
            # 根据POST参数来更新指定的字段
            if upload_traffic is not None:
                container.upload_traffic = upload_traffic_gb  # 使用GB单位
            if download_traffic is not None:
                container.download_traffic = download_traffic_gb  # 使用GB单位

            db.session.commit()

        # 7. 更新 `servers` 表中的剩余流量
        server = Server.query.filter_by(id=server_id).first()  # 修改了这里的查询条件，改为根据自增的 id 查询
        if server:
            if remaining_traffic is not None:
                server.remaining_traffic = remaining_traffic_gb  # 使用GB单位

            db.session.commit()

        db.session.commit()

        # 更新 `Rental` 表中的 traffic_usage 和 traffic_reset_date
        rental_record = Rental.query.filter_by(user_id=user_id).first()
        if rental_record:
            rental_record.traffic_usage = sum([Decimal(container.max_upload_traffic) for container in DockerContainer.query.filter_by(user_id=user_id).all()])
            rental_record.traffic_reset_date = next_month_first_day  # 设置为下个月1日
            rental_record.updated_at = datetime.utcnow()
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
