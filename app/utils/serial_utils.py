import random
import string
import logging

logging.basicConfig(level=logging.INFO)

def generate_serial_number(length=12):
    """
    生成序列号
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_bulk_serial_numbers(count, length=12):
    """
    批量生成序列号
    """
    serial_numbers = [generate_serial_number(length) for _ in range(count)]
    logging.info(f"Generated {count} serial numbers.")
    return serial_numbers
