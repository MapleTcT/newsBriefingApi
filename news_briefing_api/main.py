import logging
import database
import scheduler
import api
import time
import os
import sys

# 确保能导入同目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("news_briefing.log")
    ]
)

if __name__ == "__main__":
    logging.info("应用程序启动...")

    # 1. 初始化数据库
    try:
        database.init_db()
    except Exception as e:
        logging.critical(f"初始化数据库失败: {e}. 退出。")
        exit(1)

    # 2. 在后台线程中启动调度器
    # 调度器将立即运行第一个任务
    scheduler.run_scheduler_in_thread()

    # 给调度器线程一点时间启动
    time.sleep(2)

    # 3. 启动API服务器（这将阻塞主线程）
    # 在启动后台调度器后，在主线程中运行API
    api.run_api(debug=False)

    logging.info("应用程序完成。")  # 如果API无限期运行，可能不会达到这一行

