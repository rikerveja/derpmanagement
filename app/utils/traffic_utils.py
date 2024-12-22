import random
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟实时流量统计
def get_real_time_traffic(user_id):
    """
    模拟从监控系统获取实时流量数据。
    :param user_id: 用户 ID
    :return: 流量数据字典
    """
    try:
        current_rate = random.uniform(0.1, 10.0)  # 当前流量速率，单位 Mbps
        total_traffic = random.uniform(100.0, 500.0)  # 总流量，单位 MB
        traffic_data = {"user_id": user_id, "current_rate": current_rate, "total_traffic": total_traffic}

        logger.info(f"Retrieved real-time traffic data for user {user_id}: {traffic_data}")
        return traffic_data
    except Exception as e:
        logger.error(f"Error retrieving real-time traffic data for user {user_id}: {e}")
        return {"user_id": user_id, "error": "Failed to retrieve traffic data"}


# 检测异常流量
def detect_abnormal_traffic(user_id):
    """
    检测用户的流量是否异常（例如流量速率过高）。
    :param user_id: 用户 ID
    :return: 异常流量检测结果
    """
    try:
        traffic = get_real_time_traffic(user_id)

        # 检测异常流量（假设 8 Mbps 为异常流量的阈值）
        if traffic["current_rate"] > 8.0:
            logger.warning(f"Abnormal traffic detected for user {user_id}: {traffic}")
            return {"abnormal": True, "details": traffic}

        logger.info(f"Traffic for user {user_id} is normal: {traffic}")
        return {"abnormal": False, "details": traffic}
    except Exception as e:
        logger.error(f"Error detecting abnormal traffic for user {user_id}: {e}")
        return {"abnormal": False, "details": {"error": "Failed to detect abnormal traffic"}}
