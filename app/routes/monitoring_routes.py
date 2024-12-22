from flask import Blueprint, jsonify
import random
from datetime import datetime

# 定义蓝图
monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/api/monitoring', methods=['GET'])
def get_monitoring_status():
    """
    返回一个监控状态，模拟检查服务的健康状态
    """
    # 模拟健康检查，假设服务的健康状态通过一些实际的健康检查逻辑获取
    # 这里我们用一个随机的值来模拟服务是否健康
    health_status = "healthy" if random.random() > 0.1 else "unhealthy"

    # 模拟监控响应时间
    response_time = random.uniform(0.1, 0.5)  # 模拟响应时间在0.1到0.5秒之间

    # 当前时间戳
    timestamp = datetime.utcnow().isoformat()

    return jsonify({
        "success": True,
        "message": "Monitoring is active!",
        "health_status": health_status,
        "response_time_seconds": response_time,
        "timestamp": timestamp
    }), 200
