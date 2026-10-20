"""日志配置模块

使用 Loguru 配置应用日志
"""

import sys
from loguru import logger
from app.config import config


def setup_logger():
    """配置日志系统

    按照 Loguru 最佳实践配置全局 logger：
    1. 移除默认处理器
    2. 添加控制台输出（带颜色）
    3. 添加文件输出（按天轮转，自动压缩，异步写入）
    """
    # 移除默认处理器
    logger.remove()

    # 添加控制台输出（带颜色格式）
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="DEBUG" if config.debug else "INFO",
        colorize=True,
        backtrace=True,  # 显示完整异常栈信息
        diagnose=config.debug,  # Debug 模式下显示变量值
    )

    # 添加文件输出（按天轮转，自动压缩）
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天0点自动切割新日志文件
        retention="7 days",  # 仅保留最近7天的日志
        compression="zip",  # 过期日志自动压缩为zip
        encoding="utf-8",  # 解决中文乱码
        enqueue=True,  # 异步写入，提升性能（避免IO阻塞）
        backtrace=True,  # 显示完整异常栈信息
        diagnose=True,  # 显示变量值，便于调试
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}.{function}:{line} | {message}",
    )

setup_logger()
