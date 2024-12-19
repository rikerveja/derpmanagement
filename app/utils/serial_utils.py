import random
import string

def generate_serial_numbers(count, duration_days):
    """
    生成指定数量的序列号
    """
    serials = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        serials.append({"code": code, "duration_days": duration_days, "status": "unused"})
    return serials
