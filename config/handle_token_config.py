#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import attr
from functools import lru_cache
from common.log_handler import log


@attr.s
class HandleTokenConfig:
    # 登录 URL，默认值为 "default_login_url"
    login_url: str = attr.ib(default="default_login_url")
    # 刷新 URL，默认值为 "default_refresh_url"
    refresh_url: str = attr.ib(default="default_refresh_url")
    # 用户名，默认值为 "default_username"
    username: str = attr.ib(default="default_username")
    # 密码，默认值为 "default_password"
    password: str = attr.ib(default="default_password")
    # 默认令牌，初始值为空字符串
    default_token: str = attr.ib(default="")
    # 用于指定在相关数据中表示令牌的关键字，默认值为"token"
    token_keyword: str = attr.ib(default="token")
    # 对象池大小，默认值为 5
    pool_size: int = attr.ib(default=5)
    # 请求超时时间，默认值为 3
    request_timeout: int = attr.ib(default=3)
    # 刷新令牌检查时间间隔，默认值为 10
    refresh_token_check_interval: int = attr.ib(default=10)
    # 令牌过期时间初始值，默认为 7200
    expiry_time: str = attr.ib(default=7200)
    # 最小令牌刷新时间间隔，单位秒，默认为 300（5 分钟）
    min_time_between_refreshes: int = attr.ib(default=300)
    # 同时允许的最大令牌刷新请求数量，默认为 5
    max_concurrent_refreshes: int = attr.ib(default=5)
    # 连续刷新令牌失败次数阈值，默认为 10
    refresh_failure_attempts_threshold: int = attr.ib(default=10)
    # 当主令牌连续刷新失败一定次数后，是否自动切换到备用令牌，默认为 False
    auto_switch_backup_on_failure: bool = attr.ib(default=False)
    # 重试延迟时间的倍数因子，默认为 2
    retry_delay_multiplier: int = attr.ib(default=2)
    # 线程池大小，默认值为 10
    thread_pool_size: int = attr.ib(default=10)
    # 非令牌刷新失败情况下的请求重试最大次数，默认值为 2
    general_request_retry_attempts: int = attr.ib(default=2)
    # 令牌头部信息，默认值为 None
    token_headers: dict = attr.ib(default=None)
    # 令牌缓存清理时间间隔，默认值为 3600（1 小时）
    token_cache_cleanup_interval: int = attr.ib(default=3600)


@lru_cache
def load_config():
    try:
        with open('handle_token_config.json', mode='r') as f:
            config_data = f.read()
            return HandleTokenConfig(**json.loads(config_data))
    except Exception as e:
        log.info(f"读取登录令牌配置时出现错误：{e}, 使用默认配置")
        return HandleTokenConfig()

handle_token_config = load_config()