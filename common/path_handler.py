#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
from config.basic_config import basic_config


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 测试用例路径
TEST_CASES = os.path.join(BASE_DIR, basic_config.project, 'testcase')

# 测试用例参数 JSON 文件目录
REQUEST_FILE_DIR = os.path.join(BASE_DIR, basic_config.project, 'data')

# 日志路径
LOG_PATH = os.path.join(BASE_DIR, 'log')

# 上传文件路径
UPLOAD_FILE = os.path.join(BASE_DIR, 'resources', 'uploadtest1.png')

# HTML报告目录
HTML_REPORT_DIR = os.path.join(BASE_DIR, 'report')

# MAIL测试报告正文模板
EMAIL_REPORT_TEMPLATE = os.path.join(BASE_DIR, 'templates', 'report', 'mail.html')

