from app import db
from app.models import User, UserHistory, ACLLog
from datetime import datetime, timedelta
import logging
from app.utils.docker_utils import stop_container

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def release_expired_resources():
    """
    定期检查到期用户并释放资源
    """
    try:
        now = datetime.utcnow()
        # 查询所有到期的用户
        expired_users = User.query.filter(User.rental_expiry < now).all()

        if not expired_users:
            logger.info("No expired resources found.")
            return

        for user in expired_users:
            for container in user.containers:
                container_name = f"container_{user.id}_{container.server_id}"
                # 停止容器
                stop_container(container_name)
                db.session.delete(container)  # 删除容器

            # 创建用户历史记录
            history = UserHistory(
                user_id=user.id,
                rental_start=user.created_at,
                rental_end=user.rental_expiry,
                total_traffic=sum(container.upload_traffic + container.download_traffic for container in user.containers)
            )
            db.session.add(history)  # 添加历史记录
            db.session.delete(user)  # 删除用户

        db.session.commit()  # 提交数据库事务
        logger.info("Expired resources released successfully.")
    except Exception as e:
        db.session.rollback()  # 回滚事务
        logger.error(f"Error releasing expired resources: {e}")
        logger.error(e, exc_info=True)

def regenerate_expired_acl():
    """
    定期检查 ACL 配置到期并重新生成
    """
    try:
        now = datetime.utcnow()
        # 查询过期的 ACL 配置
        expired_acls = ACLLog.query.filter(ACLLog.created_at < now - timedelta(days=32)).all()

        if not expired_acls:
            logger.info("No expired ACLs found.")
            return

        for acl in expired_acls:
            acl.acl_version = f"v{now.strftime('%Y%m%d%H%M%S')}"  # 重新生成版本号
            acl.created_at = now  # 更新创建时间

        db.session.commit()  # 提交数据库事务
        logger.info("Expired ACLs regenerated successfully.")
    except Exception as e:
        db.session.rollback()  # 回滚事务
        logger.error(f"Error regenerating expired ACLs: {e}")
        logger.error(e, exc_info=True)
