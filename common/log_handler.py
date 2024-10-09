#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from loguru import logger
from common.path_handler import LOG_PATH
from config.basic_config import basic_config


class Logger:
    _instance = None

    @staticmethod
    def setup_logger():
        if Logger._instance is None:
            # 确保日志目录存在
            os.makedirs(LOG_PATH, exist_ok=True)
            # 日志文件名称
            log_file = os.path.join(LOG_PATH, f"{basic_config.current_time}.log")
            # 配置日志记录器
            Logger._instance = logger
            Logger._instance.add(
                log_file,
                level="INFO",
                rotation='00:00',
                retention="7 days",
                encoding='utf-8',
                enqueue=True,
                backtrace=True,
                diagnose=True
            )
        return Logger._instance

log = Logger.setup_logger()


def log_record(func):
        """
        日志装饰器，优雅地记录函数执行的前后状态。

        参数：
        func (function): 待装饰的函数对象。

        返回：
        function: 装饰后的函数，具备日志记录功能。
        """
        def wrapper(*args, **kwargs):
            log.info(f"即将进入函数 {func.__name__}, 参数为: args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            log.info(f"顺利退出函数 {func.__name__}，返回结果为：{result}")
            return result
        return wrapper