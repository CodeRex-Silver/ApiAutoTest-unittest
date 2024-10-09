import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
from typing import Callable
from functools import lru_cache
from common.log_handler import log
from config.handle_token_config import handle_token_config


# 定义令牌提供器接口
class TokenProvider:
    """
    令牌提供器的抽象接口。

    包含获取令牌、判断令牌是否过期和刷新令牌的方法。
    """
    def get_token(self) -> str:
        raise NotImplementedError

    def is_token_expired(self) -> bool:
        raise NotImplementedError

    def refresh_token(self):
        raise NotImplementedError


# 默认令牌提供器实现
class DefaultTokenProvider(TokenProvider):
    """
    默认令牌提供器的实现类。

    负责生成、管理和刷新令牌。
    """
    def __init__(self):
        # 初始化令牌为配置文件中的默认令牌，如果没有则为空字符串
        self._current_token = handle_token_config.default_token
        # 设置令牌过期时间为当前时间加上配置文件中的过期时间
        self._token_expiry_time = time.time() + handle_token_config.expiry_time
        # 记录上一次刷新令牌的时间
        self._last_refresh_timestamp = 0
        # 记录令牌刷新失败的次数
        self._refresh_failure_count = 0
        # 使用线程锁确保令牌操作的线程安全
        self._token_lock = threading.RLock()
        # 创建线程池用于异步刷新令牌
        self._executor = ThreadPoolExecutor(max_workers=handle_token_config.thread_pool_size)

    @lru_cache(maxsize=None)
    def generate_signature(self):
        """
        使用哈希算法生成签名。

        将令牌编码后进行哈希运算，返回十六进制的哈希值。
        """
        data_to_hash = self._current_token.encode()
        hashed_data = hashlib.sha256(data_to_hash).hexdigest()
        return hashed_data

    async def _async_refresh_token(self):
        """
        异步刷新令牌的内部方法。

        检查是否需要刷新令牌，如果需要则向服务器发送请求刷新令牌，
        如果请求成功则更新令牌信息，否则处理错误情况。
        """
        try:
            needs_refresh = self._should_refresh_token()
            if needs_refresh:
                signature = self.generate_signature()
                data = {'current_token': self._current_token, 'signature': signature}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url=handle_token_config.refresh_url, data=data,
                                            headers=handle_token_config.token_headers,
                                            timeout=handle_token_config.request_timeout) as response:
                        response_json = await response.json()
                        if 'error' in response_json or handle_token_config.token_keyword not in response_json:
                            raise ValueError(f'刷新 token 失败，响应内容：{response_json}')
                        else:
                            with self._token_lock:
                                new_token = response_json[handle_token_config.token_keyword]
                                self._update_current_token(new_token)
                            return new_token
            else:
                with self._token_lock:
                    return self._current_token
        except Exception as e:
            self._handle_error(e)
            # 如果刷新失败次数超过阈值且配置了自动切换备用令牌，则切换到备用令牌
            if self._refresh_failure_count >= handle_token_config.refresh_failure_attempts_threshold:
                if handle_token_config.auto_switch_backup_on_failure and handle_token_config.backup_token:
                    with self._token_lock:
                        self._current_token = handle_token_config.backup_token
                        self._token_expiry_time = time.time() + handle_token_config.expiry_time
                        log.info("主令牌刷新失败次数过多，已切换到备用令牌。")
            return await self._async_refresh_token()

    def _should_refresh_token(self):
        """
        检查是否满足令牌刷新条件。

        判断令牌是否过期或者距离上一次刷新时间超过了最小刷新时间间隔。
        """
        with self._token_lock:
            return self.is_token_expired() or (time.time() - self._last_refresh_timestamp > handle_token_config.min_time_between_refreshes)

    def _update_current_token(self, new_token):
        """
        更新令牌信息。

        更新令牌、设置新的过期时间和记录刷新时间，并将刷新失败次数重置为 0。
        """
        with self._token_lock:
            self._current_token = new_token
            self._token_expiry_time = time.time() + handle_token_config.expiry_time
            self._last_refresh_timestamp = time.time()
            self._refresh_failure_count = 0

    def _handle_error(self, e):
        """
        处理令牌刷新错误。

        记录错误日志，并根据错误类型给出相应的错误信息。
        """
        log.error(f'自动刷新令牌时出现错误：{e}')
        if isinstance(e, aiohttp.ClientError):
            log.error("网络请求出现错误，可能是连接问题或服务器故障。")
        elif isinstance(e, ValueError):
            log.error("响应数据格式错误，无法获取新令牌。")
        else:
            log.error(f"未知错误类型：{type(e)}，错误信息：{e}")


# 令牌管理器
class TokenManager:
    """
    令牌管理器类。

    负责管理令牌的获取、刷新和自动刷新任务。
    """
    def __init__(self, token_provider: DefaultTokenProvider, on_token_updated: Callable[[str], None]=None):
        self._token_provider = token_provider
        # 如果有默认令牌则将其缓存，否则为 None
        self._cached_current_token = None if not self._token_provider._current_token else self._token_provider._current_token
        self._on_token_updated = on_token_updated
        self._backup_token = self._token_provider.config.backup_token if self._token_provider.config.backup_token is not None else ""
        self._token_lock = threading.RLock()
        # 获取事件循环
        self._loop = asyncio.get_event_loop()
        # 创建自动刷新令牌的任务
        self._auto_refresh_task = self._loop.create_task(self._auto_refresh_token())

    @lru_cache(maxsize=None)
    def get_token(self) -> str:
        """
        获取令牌。

        如果缓存的令牌为空或者已过期，则尝试刷新令牌，返回有效的令牌。
        """
        with self._token_lock:
            if self._cached_current_token is None or self._token_provider.is_token_expired():
                try:
                    self._cached_current_token = self._token_provider.refresh_token()
                except Exception as e:
                    self._handle_error(e)
                    if self._backup_token:
                        self._cached_current_token = self._backup_token
                        log.info("主令牌刷新失败，已切换到备用令牌。")
            return self._cached_current_token

    def is_token_expired(self) -> bool:
        """
        判断令牌是否过期。

        如果没有设置过期时间，则默认令牌已过期。
        """
        with self._token_lock:
            return time.time() > self._token_provider._token_expiry_time if self._token_provider._token_expiry_time else True

    def refresh_token(self):
        """
        手动刷新令牌。

        调用令牌提供器的刷新方法，并在新令牌可用时通知回调函数。
        """
        new_token = self._token_provider.refresh_token()
        if new_token and self._on_token_updated:
            self._on_token_updated(new_token)
        return new_token

    async def _auto_refresh_token(self):
        """
        自动刷新令牌的异步任务。

        持续检查令牌是否过期，如果过期则尝试刷新令牌。
        """
        while True:
            if self.is_token_expired():
                try:
                    new_token = await self._token_provider._async_refresh_token()
                    if new_token:
                        self._cached_current_token = new_token
                        if self._on_token_updated:
                            self._on_token_updated(new_token)
                except Exception as e:
                    self._handle_error(e)
            await asyncio.sleep(self._token_provider.config.refresh_token_check_interval)

    def manual_refresh_token(self):
        """
        手动触发令牌刷新。

        调用刷新令牌方法并返回结果。
        """
        return self.refresh_token()

    def _handle_error(self, e):
        """
        处理令牌管理中的错误。

        记录错误日志，并根据错误类型给出相应的错误信息。
        """
        log.error(f'自动刷新令牌时出现错误：{e}')
        if isinstance(e, aiohttp.ClientError):
            log.error("网络请求出现错误，可能是连接问题或服务器故障。")
        elif isinstance(e, ValueError):
            log.error("响应数据格式错误，无法获取新令牌。")
        else:
            log.error(f"未知错误类型：{type(e)}，错误信息：{e}")


# 令牌获取器池
class TokenFetcherPool:
    """
    令牌获取器池类。

    管理多个令牌获取器，实现令牌获取器的获取、释放和并发刷新功能。
    """
    def __init__(self):
        token_provider = DefaultTokenProvider()
        self._token_fetchers = [TokenManager(token_provider) for _ in range(token_provider.config.pool_size)]
        self._lock = threading.RLock()
        # 根据实际系统负载和硬件资源调整线程池大小
        self._concurrent_refresh_executor = ThreadPoolExecutor(max_workers=max(2, token_provider.config.pool_size // 2))
        self._retry_count = 0
        self._max_retry = handle_token_config.max_retry

    def get_token_fetcher(self):
        """
        获取可用的令牌获取器。

        遍历令牌获取器池，返回一个未过期的令牌获取器，如果没有则返回 None。
        """
        with self._lock:
            for fetcher in self._token_fetchers:
                if not fetcher.is_token_expired():
                    return fetcher
            return None

    def release_token_fetcher(self, fetcher):
        """
        释放令牌获取器。

        将令牌获取器放回池中，如果不在池中则尝试刷新令牌后再放回。
        """
        with self._lock:
            if fetcher in self._token_fetchers:
                pass
            else:
                try:
                    fetcher.refresh_token()
                except Exception as e:
                    self._handle_error(e)
                self._token_fetchers.append(fetcher)

    def _can_refresh_concurrently(self):
        """
        判断是否可以并发刷新令牌。

        通过比较当前并发刷新次数和最大并发刷新次数来确定。
        """
        return self._concurrent_refresh_executor._work_queue.qsize() < self._concurrent_refresh_executor._max_workers * 2

    async def _async_refresh_token(self, fetcher):
        try:
            return fetcher.refresh_token()
        except Exception as e:
            self._handle_error(e)
            # 标记令牌获取器不可用
            fetcher.invalid = True
            if self._retry_count < self._max_retry:
                await asyncio.sleep(handle_token_config.retry_delay)
                self._retry_count += 1
                return fetcher.refresh_token()
            else:
                return None

    async def refresh_token_concurrently(self):
        """
        并发刷新令牌。

        如果可以并发刷新，则遍历令牌获取器池并发地刷新令牌。
        """
        if self._can_refresh_concurrently():
            with self._lock:
                tasks = [self._async_refresh_token(fetcher) for fetcher in self._token_fetchers]
                results = await asyncio.gather(*tasks)
                # 处理结果，如果需要的话
        else:
            log.warning("并发刷新令牌达到上限，暂不执行并发刷新。")

    def _handle_error(self, e):
        """
        处理令牌获取器池中的错误。

        记录错误日志，并根据错误类型给出相应的错误信息。
        """
        log.error(f"并发刷新令牌时出现错误：{e}")
        if isinstance(e, aiohttp.ClientError):
            log.error("网络请求出现错误，可能是连接问题或服务器故障。")
        elif isinstance(e, ValueError):
            log.error("响应数据格式错误，无法获取新令牌。")
        else:
            log.error(f"未知错误类型：{type(e)}，错误信息：{e}")

    def shutdown(self):
        """
        安全关闭令牌获取器池。

        关闭并发刷新线程池，等待所有任务完成，避免资源泄漏和潜在的死锁。
        """
        self._concurrent_refresh_executor.shutdown(wait=True)


