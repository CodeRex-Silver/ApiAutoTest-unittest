#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from common.log_handler import log
from common.path_handler import EMAIL_REPORT_TEMPLATE
from config.basic_config import basic_config


class EmailHandler:
    def __init__(self, filename):
        self.filename = filename
    
    def render_email_report(self, file=EMAIL_REPORT_TEMPLATE, **kwargs):
        """
        渲染邮箱测试报告

        :param file:
        :return:
        """
        try:
            with open(file, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            return template.render(**kwargs)
        except Exception as e:
            log.error(f'渲染邮箱测试报告失败: {e}')
            raise e

    def create_email_content(self, test_results):
        """生成邮件内容和 HTML 报告附件"""
        msg = MIMEMultipart()
        msg['Subject'] = basic_config.result_title
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
        msg['From'] = basic_config.tester_name

        # 生成邮件正文
        report_data = {
            'title': basic_config.result_title,
            'tester': basic_config.tester_name,
            'start_time': str(test_results.start_time),
            'end_time': str(test_results.end_time),
            'duration': str(test_results.duration),
            'pass': str(test_results.passed),
            'pass_rate': str(test_results.pass_rate),
            'fail': str(test_results.failed),
            'failure_rate': str(test_results.failure_rate),
            'error': str(test_results.errors),
            'error_rate': str(test_results.error_rate),
            'skip': str(test_results.skipped),
            'skip_rate': str(test_results.skip_rate),
        }
        content = self.render_email_report(**report_data)
        text_part = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(text_part)

        # 添加邮件附件
        try:
            with open(self.filename, 'rb') as f:
                attachment = MIMEText(f.read(), 'base64', 'utf-8')
            attachment['Content-Type'] = 'application/octet-stream'
            attachment_filename = os.path.basename(self.filename)
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
            msg.attach(attachment)
        except Exception as attachment_error:
            log.error(f'添加附件失败: {attachment_error}')

        return msg

    def send(self):
        """发送邮件"""
        try:
            server = basic_config.email_server
            port = basic_config.email_port
            user = basic_config.email_user
            password = basic_config.email_password
            recipients = basic_config.email_to

            use_ssl = basic_config.email_ssl
            smtp_obj = smtplib.SMTP_SSL(server, port) if use_ssl else smtplib.SMTP(server, port)

            smtp_obj.login(user, password)
            smtp_obj.sendmail(user, recipients, self.create_email_content().as_string())
            smtp_obj.quit()
        except Exception as e:
            log.error(f'测试报告邮件发送失败: {e}')
        else:
            log.info("测试报告邮件发送成功")
