from flask import Blueprint, request, jsonify 
from app.models import SerialNumber, UserContainer, UserHistory, Rental, DockerContainer, UserTraffic
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
    traffic_limit = data.get('traffic_limit', 0)  # 获取流量限制

    if not serial_code or not user_id:
        log_operation(
            user_id=None,
            operation="create_rental",
            status="failed",
            details="Missing serial code or user ID"
        )
        return jsonify({"success": False, "message": "Missing serial code or user ID"}), 400

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
        serial_number.activated_at = datetime.utcnow()
        serial_number.expires_at = datetime.utcnow() + timedelta(days=serial_number.valid_days)
        
        # 创建租赁记录
        rental = Rental(
            user_id=user_id,
            serial_number_id=serial_number.id,
            status='active',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=serial_number.valid_days),
            server_ids=[],
            container_ids=[],
            traffic_limit=traffic_limit,  # 记录流量限制
            traffic_usage=0,  # 初始流量使用为0
            serial_number_expiry=serial_number.expires_at,
            renewal_count=0
        )
        db.session.add(rental)

        # 分配容器并创建 Docker 容器记录
        docker_container = DockerContainer(
            container_id=f"container_{user_id}_{rental.id}",
            container_name=f"container_{rental.id}",
            user_id=user_id,
            server_id=1,  # 假设为服务器ID，这里可以进行进一步逻辑处理
            status="running"
        )
        db.session.add(docker_container)

        # 更新租赁关系表
        rental.container_ids = [docker_container.id]  # 将容器ID关联到租赁记录
        rental.server_ids = [1]  # 假设将该租赁与服务器ID 1 关联

        # 创建 ACL 配置
        acl_config = ACLConfig(
            user_id=user_id,
            server_ids=rental.server_ids,
            container_ids=rental.container_ids,
            acl_data={},
            version="1.0",
            is_active=True
        )
        db.session.add(acl_config)

        # 更新服务器的用户数和流量
        server = Server.query.get(1)  # 假设为服务器ID 1
        if server:
            server.user_count += 1  # 用户数增加
            server.total_traffic += traffic_limit  # 更新总流量（假设为租赁的流量限制）
            server.remaining_traffic -= traffic_limit  # 更新剩余流量（假设为租赁的流量限制）

        # 提交事务
        db.session.commit()

        log_operation(
            user_id=user_id,
            operation="create_rental",
            status="success",
            details=f"Rental created and resources assigned for user {user_id} with serial code {serial_code}"
        )

        return jsonify({"success": True, "message": "Rental created and resources assigned successfully"}), 200

    except Exception as e:
        db.session.rollback()  # 回滚事务
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

