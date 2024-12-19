from app import create_app, db

# 创建应用实例
app = create_app()

# 启动应用程序
if __name__ == "__main__":
    # 建议添加日志记录功能
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the application...")

    # 确保数据库表创建
    with app.app_context():
        db.create_all()  # 创建所有数据库表（如果尚未存在）
        logging.info("Database tables created or verified.")

    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=8000)
