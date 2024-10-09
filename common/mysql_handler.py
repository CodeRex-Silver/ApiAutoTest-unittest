#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from common.log_handler import log
from config.basic_config import basic_config


class MysqlHandler:
    def __init__(self):
        try:
            self.engine = create_engine(f"mysql+pymysql://{basic_config.db_user}:{basic_config.db_password}@{basic_config.db_host}:{basic_config.db_port}/{basic_config.db_database}?charset={basic_config.db_charset}")
            self.Session = sessionmaker(bind=self.engine)
        except BaseException as e:
            log.error(f'数据库连接失败 \n {e}')

    def execute(self, sql):
        """
        数据库操作执行

        :param sql:
        :return:
        """
        try:
            with self.Session() as session:
                session.execute(text(sql))
                session.commit()
        except Exception as e:
            session.rollback()
            log.error(f'执行 {sql} 失败: {e}')

mysql_handler = MysqlHandler()

