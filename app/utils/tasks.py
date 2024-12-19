from app import db
from app.models import User, UserHistory, ACLLog
from datetime import datetime, timedelta
import logging
from app.utils.docker_utils import stop_container

logging.basicConfig(level=logging.INFO)

def release_expired_resources():
    """
    定期检查到期用户并释放资源
    """
    now = datetime.utcnow()
    expired_users = User.query.filter(User.rental_expiry < now).all()

    for user in expired_users:
        for container in user.containers:
            container_name = f"container_{user.id}_{container.server_id}"
            stop_container(container_name)
            db.session.delete(container)

        history = UserHistory(
            user_id=user.id,
            rental_start=user.created_at,
            rental_end=user.rental_expiry,
            total_traffic=sum(container.upload_traffic + container.download_traffic for container in user.containers)
        )
        db.session.add(history)
        db.session.delete(user)

    db.session.commit()
    logging.info("Expired resources released.")

def regenerate_expired_acl():
    """
    定期检查 ACL 配置到期并重新生成
    """
    now = datetime.utcnow()
    expired_acls = ACLLog.query.filter(ACLLog.created_at < now - timedelta(days=32)).all()

    for acl in expired_acls:
        acl.acl_version = f"v{now.strftime('%Y%m%d%H%M%S')}"
        acl.created_at = now
    db.session.commit()
    logging.info("Expired ACLs regenerated.")
