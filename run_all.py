#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest
from common.log_handler import log
from XTestRunner import HTMLTestRunner
from common.email_handler import EmailHandler
from config.basic_config import basic_config
from common.path_handler import TEST_CASES, HTML_REPORT_DIR


class TestRunner:
    def __init__(self):
        self.test_case_path = TEST_CASES
        self.test_rule = 'test_*.py'

    def generate_html_report(self, filename = f"{basic_config.result_filename}_{basic_config.current_time}.html"):
        """
        生成 HTML 测试报告。
        """
        os.makedirs(HTML_REPORT_DIR, exist_ok=True)
        report_file = os.path.join(HTML_REPORT_DIR, filename)
        try:
            fp = open(report_file, 'wb')
            runner = HTMLTestRunner(
                stream=fp,
                title=basic_config.result_title,
                verbosity=2,
                tester=basic_config.tester_name,
                description=basic_config.result_description,
                language='zh-CN'
            )
            return runner, fp, report_file
        except Exception as e:
            log.error(f'创建 HTML 报告文件失败: {e}')
            raise e

    def run_tests(self):
        try:
            """
            使用 HTMLTestRunner 生成测试报告。
            """
            test_suite = unittest.defaultTestLoader.discover(self.test_case_path, self.test_rule)
            runner, fp, report_file = self.generate_html_report()
            runner.run(test_suite)
            fp.close()
        except Exception as e:
            log.error('运行异常：{}'.format(e))
            raise
        else:
            # send_email = EmailHandler(report_file)
            # send_email.send()
            log.info('测试报告生成并发送成功。')


if __name__ == '__main__':
    test_runner = TestRunner()
    test_runner.run_tests()

