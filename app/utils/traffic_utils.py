# app/utils/traffic_utils.py
import random

# 模拟实时流量统计
def get_real_time_traffic(user_id):
    # 模拟从监控系统获取流量数据
    return {"user_id": user_id, "current_rate": random.uniform(0.1, 10.0), "total_traffic": random.uniform(100.0, 500.0)}

# 检测异常流量
def detect_abnormal_traffic(user_id):
    traffic = get_real_time_traffic(user_id)
    if traffic['current_rate'] > 8.0:  # 假设 8 Mbps 是异常流量
        return {"abnormal": True, "details": traffic}
    return {"abnormal": False, "details": traffic}
