#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from core.basic_unit import Unit
from testcase.interface_manager import ManageRequests
from common.log_handler import log


class DemoAPI1(Unit):
    def test_api(self):
        respheaders, respbody, resp = ManageRequests.create_coupon()
        log.info(f"{respheaders},\n {respbody},\n {resp.text}")