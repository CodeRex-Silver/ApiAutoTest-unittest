#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from config.basic_config import basic_config
from core import *
from core.data_processor import *


@handle_json_data
class RequestData:
    # 使用装饰器处理方法，使其能够接收来自指定文件的字典数据。
    @file_data_dict(r'testcase\data\interface_data.json')
    def interface_data_with_dict(named_dict_data):
        return dict(named_dict_data)

header = basic_config.header

class PrepareRquest:
    @staticmethod
    @request_data(RequestData.interface_data_with_dict())
    def create_coupon(body_json,headers=None,body_data=None):
        headers=header
        body_json=body_json
        return headers, body_data, body_json

class ManageRequests:
    @post("/api/v1/crm/coupon-template/create")
    def create_coupon():
        return PrepareRquest.create_coupon()

