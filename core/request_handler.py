#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import time
import requests
import threading
from collections import namedtuple
from functools import lru_cache
from typing import Dict, Any, Optional, Callable
from common.log_handler import log
from config.basic_config import basic_config


class RequestHandler:
    _instance = None

    def __new__(cls):
        """
        实现单例模式的构造方法。确保在整个程序中只有一个 RequestHandler 实例。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_once()
        return cls._instance

    def _initialize_once(self):
        """
        初始化方法，仅在第一次创建实例时调用。
        """
        self._load_config()
        # 定义一个具名元组，用于表示错误响应
        self.ErrorResponse = namedtuple('ErrorResponse', ['error_code', 'error_message'])
        # 创建一个线程局部存储对象
        self._session_local = threading.local()

    def _load_config(self):
        """
        从默认配置中加载请求相关的配置参数。
        """
        # 获取默认配置
        config = basic_config
        # 设置请求的主机地址
        self.host = config.request_host
        # 设置请求的时间间隔
        self.interval = config.request_interval
        # 设置默认的请求超时时间
        self.default_timeout = config.request_timeout
        # 设置默认的请求验证标志
        self.default_verify = config.request_verify

    @lru_cache(maxsize=None)
    def _get_cached_file_obj(self, file_path: str) -> Any:
        """
        从给定的文件路径获取缓存的文件对象。如果文件不存在，则抛出错误。
        :param file_path: 文件路径。
        :return: 文件对象。
        """
        # 判断文件是否存在，若不存在则记录错误并抛出错误响应
        if not os.path.exists(file_path):
            log.error(f"文件 {file_path} 不存在。")
            raise self.ErrorResponse(error_code=-5, error_message=f'文件 {file_path} 不存在。')
        # 打开文件并返回文件对象
        with open(file_path, 'rb') as fo:
            return fo

    def _format_data(
            self, url: str, method: str, headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None, body_data: Optional[Any] = None,
            body_json: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
            ) -> Dict[str, Any]:
        """
        格式化请求数据。
        :param url: 请求 URL。
        :param method: 请求方法。
        :param headers: 请求头。
        :param params: 请求参数。
        :param body_data: 请求体数据。
        :param body_json: 请求体 JSON 数据。
        :param file_path: 文件路径（如果有文件上传）。
        :return: 格式化后的请求数据字典。
        """
        # 创建一个字典，用于存储格式化后的请求数据
        formatted_data = {
            'url': url,
            'method': method,
            'headers': headers,
            'params': params,
            'data': body_data,
            'json': body_json
        }
        if file_path:
            # 获取文件名称和扩展名
            file_name = file_path.split('/')[-1]
            file_extension = file_path.split('.')[-1]
            try:
                # 获取缓存的文件对象
                file_obj = self._get_cached_file_obj(file_path)
                # 将文件信息添加到格式化数据字典中
                formatted_data['files'] = (file_name, file_obj, file_extension)
            except Exception as e:
                # 记录处理文件时的错误
                log.error(f"处理文件时出现错误：\n{e}")
                raise ValueError(f"处理文件时出现错误：\n{e}")
        return formatted_data

    def _get_session(self, request_engine=requests) -> requests.Session:
        """
        获取会话对象。如果线程局部存储中没有会话对象或者传入的请求引擎与当前的不同，则创建新的会话对象。
        :param request_engine: 请求引擎（默认为 requests）。
        :return: 会话对象。
        """
        # 如果线程局部存储中没有会话对象或者请求引擎与当前不同，则创建新的会话对象
        if not hasattr(self._session_local, 'session') or (request_engine and self._session_local.request_engine!= request_engine):
            self._session_local.session = request_engine.Session()
            self._session_local.request_engine = request_engine
        return self._session_local.session

    def send_request(
            self, url: str, method: str, headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None, body_data: Optional[Any] = None,
            body_json: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None
            ) -> requests.Response:
        """
        发送请求。
        :param url: 请求 URL。
        :param method: 请求方法。
        :param headers: 请求头。
        :param params: 请求参数。
        :param body_data: 请求体数据。
        :param body_json: 请求体 JSON 数据。
        :param file_path: 文件路径（如果有文件上传）。
        :return: 请求响应对象。
        """
        # 格式化请求数据
        request_args = self._format_data(
            url=url,
            method=method,
            headers=headers,
            params=params,
            body_data=body_data,
            body_json=body_json,
            file_path=file_path
        )
        # 记录请求信息
        log.info(f"请求 URL: {url}")
        log.info(f"请求方法: {method}")
        if headers:
            log.info(f"请求头: {headers}")
        if params:
            log.info(f"请求参数: {params}")
        body = body_data if body_data else body_json
        if body:
            log.info(f"请求体: {body}")
        if file_path:
            log.info(f"请求文件: {file_path}")
        try:
            # 等待一段时间再发送请求
            time.sleep(self.interval)
            start_time = time.time()
            # 获取会话对象并发送请求
            with self._get_session() as session:
                response = session.request(
                    **request_args,
                    timeout=self.default_timeout,
                    verify=self.default_verify
                )
            end_time = time.time()
            # 计算响应时间并记录
            response_time = end_time - start_time
            log.info(f"请求响应状态码：{response.status_code}")
            log.info(f"响应时间：{response_time:.2f} 秒")
            log.info(f"请求响应: {response.json()}")
            return response
        except requests.exceptions.Timeout as time_error:
            # 记录请求超时错误
            log.error(f"请求超时：\n{time_error}")
            raise self.ErrorResponse(error_code=-3, error_message='请求超时')
        except requests.exceptions.HTTPError as http_error:
            # 记录 HTTP 错误
            log.error(f"HTTP 错误: \n{http_error}")
            raise self.ErrorResponse(error_code=-2, error_message='HTTP 错误')
        except requests.exceptions.RequestException as req_error:
            # 记录请求异常
            log.error(f'请求异常: \n{req_error}')
            raise self.ErrorResponse(error_code=-1, error_message=f'请求异常：{req_error}')

    def _construct_full_url(self, host: str, url: str) -> str:
        """
        构建完整的请求 URL。
        :param host: 请求主机地址。
        :param url: 请求相对路径。
        :return: 完整的请求 URL。
        """
        # 判断输入的 host 和 url 是否为字符串类型，若不是则抛出 ValueError
        if not isinstance(host, str) or not isinstance(url, str):
            raise ValueError("输入的 host 和 url 必须是字符串类型。")
        # 判断 host 和 url 是否为空，若为空则抛出 ValueError
        if not host or not url:
            raise ValueError("host 和 url 都不能为空。")
        # 去除 host 末尾的多余斜杠
        cleaned_host = re.sub('/+$', '', host)
        # 去除 url 开头的多余斜杠
        cleaned_url = re.sub('^/+', '', url)
        return f'{cleaned_host}/{cleaned_url}'

    def post(self, url: str) -> Callable:
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    # 调用被装饰的函数获取参数
                    headers, body_data, body_json = func(*args, **kwargs)
                    # 构建完整的 URL
                    full_url = self._construct_full_url(self.host, url)
                    # 发送 POST 请求并返回响应的头部、请求体和响应
                    if body_data and not body_json:
                        response = self.send_request(
                            url=full_url,
                            method="POST",
                            headers=headers,
                            body_data=body_data
                            )
                    elif body_json and not body_data:
                        response = self.send_request(
                            url=full_url,
                            method="POST",
                            headers=headers,
                            body_json=body_json
                            )
                    else:
                        log.error(f"请求 body 错误: \n表单数据:{body_data} \nJSON数据:{body_json}")
                        raise ValueError(f"请求 body 错误: \n表单数据:{body_data} \nJSON数据:{body_json}")
                    return response.headers, response.request.body, response
                except Exception as e:
                    # 如果异常是 ErrorResponse 类型，则记录错误信息，否则记录通用错误信息并抛出 ValueError
                    if isinstance(e, self.ErrorResponse):
                        log.error(f"POST 请求异常：\n{e.error_message}")
                    else:
                        log.error(f"POST 请求异常：\n{e}")
                    raise ValueError(f"POST 请求异常：\n{e}")
            return wrapper
        return decorator

    def get(self, url: str) -> Callable:
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    # 调用被装饰的函数获取参数
                    headers, id_value, params = func(*args, **kwargs)
                    # 构建完整的 URL
                    full_url = self._construct_full_url(self.host, url)
                    # 如果 URL 中包含 '{{id}}' 且 id_value 为 None，则抛出错误响应
                    if '{{id}}' in full_url and id_value is None:
                        raise self.ErrorResponse(error_code=-4, error_message='缺少 id 参数')
                    # 如果 id_value 不为 None，则将 URL 中的 '{{id}}' 替换为 id_value
                    if id_value is not None:
                        full_url = full_url.replace('{{id}}', str(id_value))
                    # 发送 GET 请求并返回响应的头部、请求体和响应
                    response = self.send_request(
                        url=full_url,
                        method='GET',
                        headers=headers,
                        params=params
                    )
                    return response.headers, response.request.body, response
                except Exception as e:
                    # 如果异常是 ErrorResponse 类型，则记录错误信息，否则记录通用错误信息并抛出 ValueError
                    if isinstance(e, self.ErrorResponse):
                        log.error(f"GET 请求异常：\n{e.error_message}")
                    else:
                        log.error(f"GET 请求异常：\n{e}")
                    raise ValueError(f"GET 请求异常：\n{e}")
            return wrapper
        return decorator

    def put(self, url: str) -> Callable:
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    # 调用被装饰的函数获取参数
                    headers, file_path = func(*args, **kwargs)
                    # 构建完整的 URL
                    full_url = self._construct_full_url(self.host, url)
                    # 发送 PUT 请求并返回响应的头部、请求体和响应
                    response = self.send_request(
                        url=full_url,
                        method='PUT',
                        headers=headers,
                        file_path=file_path
                    )
                    return response.headers, response.request.body, response
                except Exception as e:
                    # 如果异常是 ErrorResponse 类型，则记录错误信息，否则记录通用错误信息并抛出 ValueError
                    if isinstance(e, self.ErrorResponse):
                        log.error(f"PUT 请求异常：\n{e.error_message}")
                    else:
                        log.error(f"PUT 请求异常：\n{e}")
                    raise ValueError(f"PUT 请求异常：\n{e}")
            return wrapper
        return decorator

    def delete(self, url: str) -> Callable:
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    # 调用被装饰的函数获取参数
                    headers = func(*args, **kwargs)
                    # 构建完整的 URL
                    full_url = self._construct_full_url(self.host, url)
                    # 发送 DELETE 请求并返回响应的头部、请求体和响应
                    response = self.send_request(
                        url=full_url,
                        method='DELETE',
                        headers=headers
                    )
                    return response.headers, response.request.body, response
                except Exception as e:
                    # 如果异常是 ErrorResponse 类型，则记录错误信息，否则记录通用错误信息并抛出 ValueError
                    if isinstance(e, self.ErrorResponse):
                        log.error(f"DELETE 请求异常：\n{e.error_message}")
                    else:
                        log.error(f"DELETE 请求异常：\n{e}")
                    raise ValueError(f"DELETE 请求异常：\n{e}")
            return wrapper
        return decorator

    def patch(self, url: str) -> Callable:
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    # 调用被装饰的函数获取参数
                    headers, body_data, body_json = func(*args, **kwargs)
                    # 构建完整的 URL
                    full_url = self._construct_full_url(self.host, url)
                    # 发送 PATCH 请求并返回响应的头部、请求体和响应
                    response = self.send_request(
                        url=full_url,
                        method='PATCH',
                        headers=headers,
                        body_data=body_data,
                        body_json=body_json
                    )
                    return response.headers, response.request.body, response
                except Exception as e:
                    # 如果异常是 ErrorResponse 类型，则记录错误信息，否则记录通用错误信息并抛出 ValueError
                    if isinstance(e, self.ErrorResponse):
                        log.error(f"PATCH 请求异常：\n{e.error_message}")
                    else:
                        log.error(f"PATCH 请求异常：\n{e}")
                    raise ValueError(f"PATCH 请求异常：\n{e}")
            return wrapper
        return decorator