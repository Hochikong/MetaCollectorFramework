import smtplib
from email.mime.base import MIMEBase
from typing import List


class SMTPAgent(object):
    """
    基于smtplib的通用邮件发送工具

    """

    def __init__(self, host: str, port: int, user: str, passwd: str):
        """

        :param host: smtp服务器地址
        :param port: smtp服务器端口
        :param user: smtp服务器登陆用户名
        :param passwd: smtp服务器登陆密码
        """
        self._host = host
        self._port = port
        self._server = smtplib.SMTP(self._host, self._port)
        self._server.starttls()
        self.__username = user
        self.__password = passwd

        self._server.login(self.__username, self.__password)

    def send(self, sender: str, receivers: List[str], content: MIMEBase) -> bool:
        """
        发送邮件

        :param sender: 发送者邮件地址字符串
        :param receivers: 接收者邮件地址列表
        :param content: 邮件内容，类型可为MIMEText或者MIMEMultipart等MIMEBase的子类型
        :return:
        """
        try:
            self._server.sendmail(sender, receivers, content.as_string())
            return True
        except smtplib.SMTPException as e:
            print("Error: 无法发送邮件, {}".format(e))
            return False

    def dispose(self):
        self._server.quit()
