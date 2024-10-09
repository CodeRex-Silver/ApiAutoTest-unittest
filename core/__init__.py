#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.request_handler import RequestHandler
from core.data_converter import DataConverter


converter = DataConverter()

# 创建请求处理实例
__request_handler = RequestHandler()


def post(url):
    """发送 POST 请求。"""
    return __request_handler.post(url)

def get(url):
    """发送 GET 请求。"""
    return __request_handler.get(url)


def put(url):
    """发送 PUT 请求。"""
    return __request_handler.put(url)


def delete(url):
    """发送 DELETE 请求。"""
    return __request_handler.delete(url)


def patch(url):
    """发送 PATCH 请求。"""
    return __request_handler.patch(url)


def basic_request(url, method, headers=None, params=None, body_data=None, body_json=None, file_path=None):
    """
    发送基本请求。可以指定请求的 URL、方法、请求头、请求参数、请求体数据、请求体 JSON 和文件路径。
    :param url: 请求的 URL。
    :param method: 请求方法，如 'GET'、'POST'、'PUT'、'DELETE'、'PATCH'。
    :param headers: 请求头，可为 None。
    :param params: 请求参数，可为 None。
    :param body_data: 请求体数据，可为 None。
    :param body_json: 请求体 JSON 数据，可为 None。
    :param file_path: 文件路径（如果有文件上传），可为 None。
    """
    return __request_handler.send_request(
        url=url,
        method=method,
        headers=headers,
        params=params,
        body_data=body_data,
        body_json=body_json,
        file_path=file_path
    )

