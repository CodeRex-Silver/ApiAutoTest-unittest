#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from common.log_handler import log


class Unit(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:
        log.info(f'Running test case: {self._testMethodName}.')

    def tearDown(self) -> None:
        log.info('Test case ended.')

