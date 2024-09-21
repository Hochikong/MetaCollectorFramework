# -*- coding: utf-8 -*-
# @Time    : 2022/5/21 19:35
# @Author  : Hochikong
# @FileName: AbstracExtension.py

from abc import ABCMeta, abstractmethod


class AbstractDriver(metaclass=ABCMeta):
    """
    驱动的抽象基类

    """

    @abstractmethod
    def prepare(self, instance: any, file_dict: dict, **kwargs) -> tuple:
        """
        初始化阶段

        :param instance: 任意一个取数代码的实例对象
        :param file_dict: 以字典形式对配置文件输入，文件内容需要插件来实现支持
        :param kwargs: 返回长度为2的元组，当执行成功时，返回的元组中，第一个元素表示操作成功与否，第二个元素表示相关的信息，
                      例如：(True, "prepare阶段成功"), (False, "prepare阶段失败，原因为xxxx")
        :return:
        """
        pass

    @abstractmethod
    def handle(self) -> tuple:
        """
        实际的执行阶段

        :return: 返回长度为2的元组，当执行成功时，返回的元组中，第一个元素表示操作成功与否，第二个元素表示相关的信息，
                例如：(True, "prepare阶段成功"), (False, "prepare阶段失败，原因为xxxx")
        """
        pass

    @abstractmethod
    def final(self) -> tuple:
        """
        收尾阶段

        :return: 返回长度为2的元组，当执行成功时，返回的元组中，第一个元素表示操作成功与否，第二个元素表示相关的信息，
                例如：(True, "prepare阶段成功"), (False, "prepare阶段失败，原因为xxxx")
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        插件的唯一名称

        :return:
        """
        pass

    @abstractmethod
    def continue_mode(self, on: bool = False) -> bool:
        """
        设置是否启用continue mode，当启用此mode的时候，插件将不会执行任何登陆或登出操作，直接执行取数

        插件内该mode默认应为False
        :param on:
        :return:
        """
        pass

    @abstractmethod
    def get_plugin_info(self) -> dict:
        """
        获取插件的相关信息统计，具体内容由插件自身实现

        :param on:
        :return:
        """
        pass
