import random
import string
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_serial_number(length=12):
    """
    生成单个序列号
    :param length: 序列号长度（默认为 12）
    :return: 随机生成的序列号
    """
    try:
        serial_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        logger.info(f"Generated serial number: {serial_number}")
        return serial_number
    except Exception as e:
        logger.error(f"Error generating serial number: {str(e)}")
        return None


def generate_bulk_serial_numbers(count, length=12):
    """
    批量生成序列号
    :param count: 生成的序列号数量
    :param length: 每个序列号的长度（默认为 12）
    :return: 序列号列表
    """
    try:
        serial_numbers = [generate_serial_number(length) for _ in range(count)]
        logger.info(f"Generated {count} serial numbers successfully.")
        return serial_numbers
    except Exception as e:
        logger.error(f"Error generating bulk serial numbers: {str(e)}")
        return []
