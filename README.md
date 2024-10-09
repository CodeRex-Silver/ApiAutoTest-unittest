# ApiAutoTest-unittest

## 介绍
Python3+unittest+requests实现的接口自动化测试框架

## 软件架构

####通用模块（common）：
1.email_handler.py：用于处理电子邮件相关的操作，比如发送邮件通知等。
2.log_handler.py：负责日志记录，方便追踪程序运行状态和错误信息。
3.mysql_handler.py：用于与 MySQL 数据库进行交互的工具类。
4.path_handler.py：用于处理文件路径相关的操作。

####配置模块（config）：
1.basic_config.py：包含基本的配置信息。
2.handle_token_config.json 和 handle_token_config.py：用于与令牌（token）处理相关的配置。

####核心模块（core）：
1.basic_unit.py：定义了一些基本的单元或基础类。
2.data_converter.py：用于数据转换的模块。
3.data_processor.py：核心的数据处理模块。
4.token_handler.py：处理令牌相关的业务逻辑。
5.request_handler.py: 处理请求相关的业务逻辑。

####主程序和测试模块：
1.run_all.py、run_class.py 和 run_thread.py：不同的运行入口。
2.templates/report/mail.html：用于生成邮件报告的模板文件。
3.testcase/data/interface_data.json：接口测试数据文件。
4.testcase/interface_manager.py 和 testcase/testcase/test_api.py：用于接口测试的模块。
5.requirements.txt：项目依赖包。
