#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from testcase.testcase.test_api import DemoAPI1


class TestRunner:
    def __init__(self):
        self.loader = unittest.TestLoader()

    def run_tests(self, testcase_classes, verbosity=2):
        """
        :param testcase_classes: 引入的类名列表
        :param verbosity: 输出详细程度
        """
        suite = unittest.TestSuite()
        for testcase_class in testcase_classes:
            tests = self.loader.loadTestsFromTestCase(testcase_class)
            suite.addTests(tests)

        runner = unittest.TextTestRunner(verbosity=verbosity)
        runner.run(suite)


if __name__ == '__main__':
    run_class = TestRunner()
    run_class.run_tests([
        DemoAPI1
    ])
