#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import attr
import json
from datetime import datetime
from functools import lru_cache


@attr.s
class Config:
    # 项目名称，默认值为'test'
    project: str = attr.ib(default='testcase')
    # 测试人员名称，默认值为'CodeRex'
    tester_name: str = attr.ib(default='CodeRex')
    # 结果文件名，默认值为'report'
    result_filename: str = attr.ib(default='report')
    # 结果标题，默认值为'test report'
    result_title: str = attr.ib(default='test report')
    # 结果描述，默认值为'api auto test'
    result_description: str = attr.ib(default='api auto test')

    # 请求头，默认值是'mock:.....'
    header: str = attr.ib(default='mock:.....')
    # 请求的主机地址，默认值为'https://your_host.com'
    request_host: str = attr.ib(default='https://your_host.com')
    # 请求超时时间，默认值为 5
    request_timeout: int = attr.ib(default=5)
    # 请求间隔时间，默认值为 0.5
    request_interval: float = attr.ib(default=0.5)
    # 请求是否验证，默认值为 False
    request_verify: bool = attr.ib(default=True)

    # 数据库主机地址，默认值为'127.0.0.1'
    db_host: str = attr.ib(default='127.0.0.1')
    # 数据库端口号，默认值为 3306
    db_port: int = attr.ib(default=3306)
    # 数据库用户名，默认值为'root'
    db_user: str = attr.ib(default='root')
    # 数据库密码，默认值为'123456'
    db_password: str = attr.ib(default='123456')
    # 数据库名称，默认值为'auto_api'
    db_database: str = attr.ib(default='auto_api')
    # 数据库字符集，默认值为'utf8mb4'
    db_charset: str = attr.ib(default='utf8mb4')

    # 邮件服务器地址，默认值为'smtp.qq.com'
    email_server: str = attr.ib(default='smtp.qq.com')
    # 邮件服务器端口号，默认值为 465
    email_port: int = attr.ib(default=465)
    # 发件人邮箱地址，默认值为'123@qq.com'
    email_user: str = attr.ib(default='123@qq.com')
    # 发件人邮箱密码，默认值为'********'
    email_password: str = attr.ib(default='********')
    # 收件人邮箱列表，默认值为['********']
    email_to: list = attr.ib(default=['********'])
    # 邮件是否使用 SSL，默认值为 False
    email_ssl: bool = attr.ib(default=False)
    # 当前时间，格式为'年-月-日-时分秒微秒'，默认值为当前时间
    current_time: str = attr.ib(default=str(datetime.now().strftime('%Y-%m-%d-%H%M%S%f')))


@lru_cache
def _load_config():
    try:
        with open('basic_config.json', mode='r') as f:
            config_data = f.read()
            return Config(**json.loads(config_data))
    except Exception as e:
        print(f"读取配置时出现错误：{e}, 使用默认配置")
        return Config()

basic_config = _load_config()

