#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from concurrent.futures.thread import ThreadPoolExecutor
from common.path_handler import TEST_CASES


class TestRunner:
    def __init__(self, thread_num=8):
        self.thread_num = thread_num
        self.test_case_path = TEST_CASES
        self.test_rule = 'test_*.py'

    def run_tests(self):
        test_suite = unittest.defaultTestLoader.discover(self.test_case_path, self.test_rule)
        results = []
        with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
            for test_case in test_suite:
                def run_case_and_collect_result():
                    test_result = unittest.TestResult()
                    test_case.run(result=test_result)
                    return test_result
                results.append(executor.submit(run_case_and_collect_result))
        final_result = unittest.TestResult()
        for future in results:
            test_result = future.result()
            final_result.testsRun += test_result.testsRun
            final_result.failures.extend(test_result.failures)
            final_result.errors.extend(test_result.errors)
            final_result.skipped.extend(test_result.skipped)
            final_result.expectedFailures.extend(test_result.expectedFailures)
            final_result.unexpectedSuccesses.extend(test_result.unexpectedSuccesses)
        return final_result


if __name__ == '__main__':
    runner = TestRunner()
    result = runner.run_tests()
    print(result)
