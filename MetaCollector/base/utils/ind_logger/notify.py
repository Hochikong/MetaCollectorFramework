from notifiers.logging import NotificationHandler
from notifiers.providers.email import *


class EmailNotifier(SMTP):
    """
    基于notifiers的email provider基础实现的新的Email Provider，
    建议使用QQ邮箱，成功率会比较高（比网易高很多）

    可以调用实例的notify方法实现邮件发送

    局限性：
    1.无法抄送
    2.对复杂的邮件内容支持不佳
    """

    def _connect_to_server(self, data: dict):
        self.smtp_server = None
        if data["ssl"]:
            self.smtp_server = smtplib.SMTP_SSL()
        else:
            self.smtp_server = smtplib.SMTP()
        self.configuration = self._get_configuration(data)
        self.smtp_server.connect(data["host"], data["port"])
        if data["tls"] and not data["ssl"]:
            self.smtp_server.ehlo()
            self.smtp_server.starttls()

        if data["login"] and data.get("username"):
            self.smtp_server.login(data["username"], data["password"])


class NotificationHandlerNew(NotificationHandler):
    def init_providers(self, provider, kwargs):
        self.provider = EmailNotifier()


class EmailNotifierWrapper(object):
    def __init__(self, host: str, user: str, passwd: str, sender: str, subject: str, receiver: str):
        self.smtp_host = host
        self.__username = user
        self.__password = passwd
        self.__sender = sender
        self.__subject = subject
        self.__receiver = receiver
        self.en = EmailNotifier()

    def update_subject(self, new_value: str):
        """
        更新主题，旧的主题将会自动备份（覆盖上一个备份）

        :param new_value: 新的邮件主题
        :return:
        """
        self.__subject = new_value

    def get_subject(self) -> str:
        return self.__subject

    def quick_send(self, content):
        """
        简化notifier的使用

        :param content: 邮件内容，字符串
        :return:
        """
        self.en.notify(host=self.smtp_host,
                       username=self.__username,
                       password=self.__password,
                       to=self.__receiver,
                       message=content,
                       from_=self.__sender,
                       subject=self.__subject
                       )

    def send(self, sender, subject, receiver, content):
        """
        简化notifier的使用

        :param sender: 发送者邮件地址，字符串
        :param subject: 主题
        :param receiver: 接收者，单个邮件地址，字符串
        :param content: 邮件内容，字符串
        :return:
        """
        self.en.notify(host=self.smtp_host,
                       username=self.__username,
                       password=self.__password,
                       to=receiver,
                       message=content,
                       from_=sender,
                       subject=subject
                       )
