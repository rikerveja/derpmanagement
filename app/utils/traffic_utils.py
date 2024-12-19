# app/utils/traffic_utils.py
import random

# ģ��ʵʱ����ͳ��
def get_real_time_traffic(user_id):
    # ģ��Ӽ��ϵͳ��ȡ��������
    return {"user_id": user_id, "current_rate": random.uniform(0.1, 10.0), "total_traffic": random.uniform(100.0, 500.0)}

# ����쳣����
def detect_abnormal_traffic(user_id):
    traffic = get_real_time_traffic(user_id)
    if traffic['current_rate'] > 8.0:  # ���� 8 Mbps ���쳣����
        return {"abnormal": True, "details": traffic}
    return {"abnormal": False, "details": traffic}
