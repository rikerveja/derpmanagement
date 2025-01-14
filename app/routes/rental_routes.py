from flask import Blueprint, request, jsonify 
from app.models import SerialNumber, UserContainer, UserHistory, Rental, DockerContainer, UserTraffic, Server
from app.utils.email_utils import send_verification_email
from app.utils.logging_utils import log_operation
from app import db
from datetime import datetime, timedelta

# 定义蓝图
rental_bp = Blueprint('rental', __name__)

@rental_bp.route('/api/rental/create', methods=['POST'])
def create_rental():
    """
    创建租赁关系，激活序列号并为用户分配服务器、容器、ACL配置等资源
    """
    data = request.json
    serial_code = data.get('serial_code')  # 获取序列号
    user_id = data.get('user_id')  # 获取用户ID
    server_id = data.get('server_id')  # 获取服务器ID
    container_id = data.get('container_id')  # 获取容器ID
    traffic_limit = data.get('traffic_limit', 0)  # 获取流量限制
    container_config = data.get('container_config', {})  # 获取容器配置（如带宽限制）

    if not serial_code or not user_id or not server_id or not container_id:
        log_operation(
            user_id=None,
            operation="create_rental",
            status="failed",
            details="Missing required fields: serial_code, user_id, server_id, or container_id"
        )
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        # 查找对应的序列号
        serial_number = SerialNumber.query.filter_by(code=serial_code, status='unused').first()
        if not serial_number:
            log_operation(
                user_id=None,
                operation="create_rental",
                status="failed",
                details=f"Invalid or used serial code: {serial_code}"
            )
            return jsonify({"success": False, "message": "Invalid or used serial code"}), 404

        # 激活序列号并更新状态
        serial_number.status = 'used'
        serial_number.user_id = user_id
        serial_number.start_date = datetime.utcnow()
        serial_number.end_date = datetime.utcnow() + timedelta(days=serial_number.valid_days)
        serial_number.used_at = datetime.utcnow()  # 更新使用时间
        
        # 创建租赁记录
        rental = Rental(
            id=None,
            user_id=user_id,
            tenant_id=None,
            serial_number_id=serial_number.id,
            serial_number_expiry=serial_number.end_date,
            status='active',
            payment_status='pending',
            payment_date=None,
            start_date=serial_number.start_date,
            end_date=serial_number.end_date,
            expired_at=None,
            traffic_limit=traffic_limit,
            traffic_usage=0,
            traffic_reset_date=None,
            renewal_count=0,
            renewed_at=None,
            container_status='active',
            server_status='active',
            server_ids=[server_id],
            container_ids=[container_id],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(rental)

        # 更新容器信息
        docker_container = DockerContainer.query.get(container_id)
        if docker_container:
            docker_container.status = "running"
            docker_container.user_id = user_id

        # 更新服务器的用户数
        server = Server.query.get(server_id)  # 查询 `servers` 表
        if server:
            server.user_count += 1

        # 提交事务
        db.session.commit()

        log_operation(
            user_id=user_id,
            operation="create_rental",
            status="success",
            details=f"Rental created for user {user_id} with serial code {serial_code}"
        )

        return jsonify({"success": True, "message": "Rental created successfully"}), 200

    except Exception as e:
        db.session.rollback()
        log_operation(
            user_id=None,
            operation="create_rental",
            status="failed",
            details=f"Error creating rental: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


@rental_bp.route('/api/rental/renew', methods=['POST'])
def renew_rental():
    """
    用户续费接口
    """
    data = request.json
    serial_code = data.get('serial_code')  # 获取序列号
    renewal_amount = data.get('renewal_amount')  # 获取续费金额
    renewal_period = data.get('renewal_period')  # 获取续费时长

    if not serial_code or not renewal_amount or not renewal_period:
        log_operation(
            user_id=None,
            operation="renew_rental",
            status="failed",
            details="Missing serial code, renewal amount, or renewal period"
        )
        return jsonify({"success": False, "message": "Missing required data"}), 400

    try:
        # 查找对应的序列号
        serial_number = SerialNumber.query.filter_by(code=serial_code, status='used').first()
        if not serial_number:
            log_operation(
                user_id=None,
                operation="renew_rental",
                status="failed",
                details=f"Invalid serial code: {serial_code}"
            )
            return jsonify({"success": False, "message": "Invalid serial code"}), 404
        
        # 查找用户的租赁记录
        rental = Rental.query.filter_by(user_id=serial_number.user_id, serial_number_id=serial_number.id, status='active').first()
        if not rental:
            log_operation(
                user_id=None,
                operation="renew_rental",
                status="failed",
                details=f"No active rental found for serial code: {serial_code}"
            )
            return jsonify({"success": False, "message": "No active rental found"}), 404

        # 增加续租天数
        rental.end_date += timedelta(days=renewal_period)
        rental.renewal_count += 1
        
        # 记录续费信息
        renewal_record = RenewalRecord(
            user_id=serial_number.user_id,
            serial_number_id=serial_number.id,
            renewal_amount=renewal_amount,
            renewal_period=renewal_period,
            renewal_date=datetime.utcnow(),
            status='success'  # 假设续费成功
        )
        db.session.add(renewal_record)

        # 提交租赁和续费记录更新
        db.session.commit()

        log_operation(
            user_id=rental.user_id,
            operation="renew_rental",
            status="success",
            details=f"Rental renewed successfully for serial code {serial_code}"
        )

        return jsonify({"success": True, "message": "Rental renewed successfully"}), 200

    except Exception as e:
        db.session.rollback()  # 回滚事务
        log_operation(
            user_id=None,
            operation="renew_rental",
            status="failed",
            details=f"Error renewing rental: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

# 获取即将到期的租赁
@rental_bp.route('/api/rental/get_expiring_rentals', methods=['GET'])
def get_expiring_rentals():
    """
    获取即将到期的租赁
    """
    try:
        # 获取查询参数 days_to_expiry，默认为7天
        days_to_expiry = request.args.get('days_to_expiry', 7, type=int)
        
        # 查找所有即将到期的租赁
        expiring_rentals = Rental.query.filter(
            Rental.status == 'active',
            Rental.end_date <= datetime.utcnow() + timedelta(days=days_to_expiry)
        ).all()

        rental_data = [
            {
                "id": rental.id,
                "user_id": rental.user_id,
                "serial_code": rental.serial_number.code if rental.serial_number else '',
                "end_date": rental.end_date,
                "days_remaining": (rental.end_date - datetime.utcnow()).days,
                "renewal_count": rental.renewal_count,
                "status": rental.status
            } for rental in expiring_rentals
        ]
        
        return jsonify({"success": True, "rentals": rental_data}), 200
    except Exception as e:
        log_operation(
            user_id=None,
            operation="get_expiring_rentals",
            status="failed",
            details=f"Error fetching expiring rentals: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 发送租赁到期通知
@rental_bp.route('/api/rental/send_expiry_notifications', methods=['POST'])
def send_expiry_notifications():
    """
    发送即将到期的租赁通知
    """
    days_to_expiry = request.json.get('days_to_expiry', 7)
    try:
        expiring_rentals = Rental.query.filter(
            Rental.status == 'active',
            Rental.end_date <= datetime.utcnow() + timedelta(days=days_to_expiry)
        ).all()

        if not expiring_rentals:
            log_operation(user_id=None, operation="send_expiry_notification", status="info", details="No rentals expiring soon.")
        
        failed_emails = []
        for rental in expiring_rentals:
            user_email = rental.user.email
            notification_type = 'first' if rental.renewal_count == 0 else 'last'
            email_sent = send_verification_email(user_email, notification_type)  # 根据通知类型发送邮件

            if not email_sent:
                failed_emails.append(user_email)

            log_operation(
                user_id=rental.user_id,
                operation="send_expiry_notification",
                status="success",
                details=f"Expiry notification sent to {user_email}"
            )

        if failed_emails:
            return jsonify({"success": False, "message": f"Failed to send reminders to: {', '.join(failed_emails)}"}), 500

        return jsonify({"success": True, "message": "Expiry notifications sent successfully"}), 200
    except Exception as e:
        log_operation(
            user_id=None,
            operation="send_expiry_notification",
            status="failed",
            details=f"Error sending expiry notifications: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Error sending notifications: {str(e)}"}), 500


# 检查并处理到期租赁
@rental_bp.route('/api/rental/check_expiry', methods=['GET'])
def check_expiry():
    """
    检测租赁到期的用户并释放资源
    """
    try:
        # 查找所有已到期的租赁
        expired_rentals = Rental.query.filter(
            Rental.status == 'active',
            Rental.end_date < datetime.utcnow()
        ).all()

        if not expired_rentals:
            log_operation(user_id=None, operation="rental_expiry", status="info", details="No expired rentals found.")
        
        for rental in expired_rentals:
            # 标记为到期
            rental.status = 'expired'

            # 删除用户的容器
            user_containers = DockerContainer.query.filter_by(user_id=rental.user_id).all()
            for container in user_containers:
                db.session.delete(container)

            # 删除用户的流量记录
            user_traffic = UserTraffic.query.filter_by(user_id=rental.user_id).all()
            for traffic in user_traffic:
                db.session.delete(traffic)

            # 删除租赁历史记录
            user_history = UserHistory.query.filter_by(user_id=rental.user_id).all()
            for history in user_history:
                db.session.delete(history)

            log_operation(
                user_id=rental.user_id,
                operation="rental_expiry",
                status="success",
                details=f"Rental expired for user {rental.user_id} and resources released"
            )

        db.session.commit()
        return jsonify({"success": True, "message": "Expired rentals processed successfully"}), 200
    except Exception as e:
        db.session.rollback()  # 回滚事务
        log_operation(
            user_id=None,
            operation="rental_expiry",
            status="failed",
            details=f"Error processing expired rentals: {str(e)}"
        )
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 查询用户租赁历史记录
@rental_bp.route('/api/rental/history/<int:user_id>', methods=['GET'])
def get_user_history(user_id):
    """
    查询用户租赁历史记录
    """
    try:
        user_rentals = Rental.query.filter_by(user_id=user_id).all()
        if not user_rentals:
            return jsonify({"success": False, "message": "No rental history found"}), 404

        history_data = [
            {
                "start_date": rental.start_date,
                "end_date": rental.end_date,
                "status": rental.status,
                "payment_status": rental.payment_status,
                "total_traffic": rental.traffic_usage,
                "renewal_count": rental.renewal_count
            } for rental in user_rentals
        ]
        return jsonify({"success": True, "history": history_data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error fetching user history: {str(e)}"}), 500
