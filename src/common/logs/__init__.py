"""日志模块

提供 Agent 的日志记录功能
"""

import logging
import os
from typing import Optional


class Logger:
    """日志记录器"""

    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "Agent") -> logging.Logger:
        """获取日志记录器（单例模式）"""
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance

    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # 创建 logs 目录（如果不存在）
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 文件处理器
        log_file = os.path.join(log_dir, "agent.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @classmethod
    def info(cls, message: str):
        """记录信息级别日志"""
        logger = cls.get_logger()
        logger.info(message)

    @classmethod
    def error(cls, message: str):
        """记录错误级别日志"""
        logger = cls.get_logger()
        logger.error(message)

    @classmethod
    def debug(cls, message: str):
        """记录调试级别日志"""
        logger = cls.get_logger()
        logger.debug(message)

    @classmethod
    def warning(cls, message: str):
        """记录警告级别日志"""
        logger = cls.get_logger()
        logger.warning(message)
