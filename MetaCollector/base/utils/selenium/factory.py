import json
import os
import time
from functools import reduce
from typing import List
import subprocess

import psutil
# import seleniumwire.undetected_chromedriver as ucw
# uc升级到3.1.0
# import undetected_chromedriver.v2 as uc
import undetected_chromedriver as uc
import yaml
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
# from seleniumwire import webdriver


def chrome_factory(driver_path: str,
                   addition_arguments: List[str],
                   pref: dict = None,
                   headless: bool = False,
                   beta_hide_info: bool = False
                   ) -> Chrome:
    """构建浏览器的工厂函数

    :param driver_path: webdriver路径
    :param addition_arguments: 附加参数列表，会被add_argument添加到Options中用于实例的创建
    :param pref: Chrome experimental_option
    :param headless: 是否以无头模式启动
    :param beta_hide_info: 是否使用beta版本的浏览器信息隐藏方法
    :return: selenium.webdriver.Chrome
    """
    chrome_options = Options()
    for opts in addition_arguments:
        chrome_options.add_argument(opts)
    if headless and '--headless' not in addition_arguments:
        chrome_options.add_argument('--headless')

    if pref is not None:
        if len(pref.keys()) > 0:
            chrome_options.add_experimental_option("prefs", pref)

    if beta_hide_info:
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

    # selenium 4.10.0 not support 'driver_executable_path' anymore
    # return Chrome(executable_path=driver_path, options=chrome_options)
    return Chrome(options=chrome_options)


class ChromeFactoryRemote(object):
    def __init__(self):
        self.cmd_procs = {}

    def get_browser(self, chrome_executable_path: str, debug_port: int, user_data_dir: str) -> str:
        """
        以远程调试模式启动浏览器
        :param chrome_executable_path: 如果在windows上，需要把chrome.exe的路径添加到path里
        :param debug_port:
        :param user_data_dir:
        :return:
        """
        cmd = self.__get_browser_init(chrome_executable_path, debug_port, user_data_dir)
        return cmd

    def __get_browser_init(self, chrome_executable_path, debug_port, user_data_dir):
        cmd = f'{chrome_executable_path} --remote-debugging-port={debug_port} --user-data-dir={user_data_dir}'
        self.cmd_procs[cmd] = subprocess.Popen(cmd, shell=True)
        return cmd

    def kill_browser(self, proc_key: str):
        proc = self.cmd_procs.get(proc_key)
        if proc is not None:
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                child.kill()
        self.cmd_procs.pop(proc_key)

    def kill_all(self):
        cmds = list(self.cmd_procs.keys())
        for k in cmds:
            self.kill_browser(k)

    @staticmethod
    def chrome_factory_remote(host: str, port: int,
                              addition_arguments: List[str],
                              pref: dict = None,
                              beta_hide_info: bool = False) -> Chrome:
        chrome_options = Options()
        for opts in addition_arguments:
            if 'user-data-dir' in opts:
                continue
            chrome_options.add_argument(opts)

        # 远程debug的chrome不支持此刻添加prefs，需要手动编辑该user_data_dir对应profile的下载目录

        # if pref is not None:
        #     if len(pref.keys()) > 0:
        #         chrome_options.add_experimental_option("prefs", pref)

        if beta_hide_info:
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("debuggerAddress", f"{host}:{port}")

        return Chrome(options=chrome_options)


# def chrome_factory_wire(driver_path: str,
#                         addition_arguments: List[str],
#                         pref: dict = None,
#                         headless: bool = False,
#                         beta_hide_info: bool = False
#                         ) -> Chrome:
#     """构建浏览器的工厂函数，配合selenium wire使用（现在可以使用undetected chromedriver，测试版本）
#
#     :param driver_path: webdriver路径
#     :param addition_arguments: 附加参数列表，会被add_argument添加到Options中用于实例的创建
#     :param pref: Chrome experimental_option
#     :param headless: 是否以无头模式启动
#     :param beta_hide_info: 是否使用beta版本的浏览器信息隐藏方法
#     :return: selenium.webdriver.Chrome
#     """
#     # chrome_options = Options()
#     chrome_options = ucw.ChromeOptions()
#     for opts in addition_arguments:
#         chrome_options.add_argument(opts)
#     if headless and '--headless' not in addition_arguments:
#         chrome_options.add_argument('--headless')
#
#     if pref is not None:
#         if len(pref.keys()) > 0:
#             chrome_options.add_experimental_option("prefs", pref)
#
#     if beta_hide_info:
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option("useAutomationExtension", False)
#
#     # use memory to storage requests with limit
#     options = {
#         'request_storage': 'memory',
#         'request_storage_max_size': 50  # Store no more than 50 requests in memory
#     }
#
#     # return webdriver.Chrome(executable_path=driver_path, options=chrome_options, seleniumwire_options=options)
#     # selenium 4.10.0 not support 'driver_executable_path' anymore
#     return webdriver.Chrome(options=chrome_options, seleniumwire_options=options)


# def chrome_factory_wireV2(driver_path: str,
#                           addition_arguments: List[str],
#                           pref: dict = None,
#                           headless: bool = False,
#                           beta_hide_info: bool = False
#                           ) -> Chrome:
#     """
#     2022-04-21 随着selenium wire与undetected chromedriver升级的适配版本
#
#     构建浏览器的工厂函数，配合selenium wire使用（现在可以使用undetected chromedriver，测试版本）
#
#     :param driver_path: webdriver路径
#     :param addition_arguments: 附加参数列表，会被add_argument添加到Options中用于实例的创建
#     :param pref: Chrome experimental_option
#     :param headless: 是否以无头模式启动
#     :param beta_hide_info: 是否使用beta版本的浏览器信息隐藏方法
#     :return: selenium.webdriver.Chrome
#     """
#     chrome_options = ucw.ChromeOptions()
#     for opts in addition_arguments:
#         chrome_options.add_argument(opts)
#     if headless and '--headless' not in addition_arguments:
#         chrome_options.add_argument('--headless')
#
#     # bypass cloudflare patch (available since 202308)
#     chrome_options.add_argument("--auto-open-devtools-for-tabs")
#     chrome_options.add_argument("--disable-popup-blocking")
#     chrome_options.browser_executable_path = str(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
#
#     if pref is not None:
#         if len(pref.keys()) > 0:
#             chrome_options.add_experimental_option("prefs", pref)
#
#     if beta_hide_info:
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option("useAutomationExtension", False)
#
#     # use memory to storage requests with limit
#     options = {
#         'request_storage': 'memory',
#         'request_storage_max_size': 50  # Store no more than 50 requests in memory
#     }
#
#     # return webdriver.Chrome(executable_path=driver_path, options=chrome_options, seleniumwire_options=options)
#     # selenium 4.10.0 not support 'driver_executable_path' anymore
#     return webdriver.Chrome(options=chrome_options, seleniumwire_options=options)


def chrome_factory_uc(driver_path: str,
                      addition_arguments: List[str],
                      pref: dict = None,
                      version: int = 90,
                      headless: bool = False,
                      beta_hide_info: bool = False
                      ) -> Chrome:
    """构建浏览器的工厂函数，现在可以使用undetected chromedriver，测试版本
       备注：不支持prefs参数，不打算支持headless，下载路径需要在浏览器中指定

    :param driver_path: webdriver路径
    :param addition_arguments: 附加参数列表，会被add_argument添加到Options中用于实例的创建
    :param pref: Chrome experimental_option
    :param version: chrome版本，需要user-agent与它与chromedriver版本均一致
    :param headless: 是否以无头模式启动
    :param beta_hide_info: 是否使用beta版本的浏览器信息隐藏方法
    :return: selenium.webdriver.Chrome
    """
    chrome_options = uc.ChromeOptions()
    for opts in addition_arguments:
        chrome_options.add_argument(opts)

    # driver = uc.Chrome(driver_executable_path=driver_path, options=chrome_options, version_main=version)
    # selenium 4.10.0 not support 'driver_executable_path' anymore
    driver = uc.Chrome(options=chrome_options, version_main=version)

    download_params = {
        "behavior": "allow",
        "downloadPath": pref['download.default_directory']
        # "downloadPath": '/home/vncuser/Downloads/sycm110'
    }

    driver.execute_cdp_cmd("Page.setDownloadBehavior", download_params)

    return driver


def yaml_loader(path: str, encoding: str = 'utf-8') -> dict:
    """用于减少yaml配置文件读取的重复代码

    :param path: 文件的路径
    :param encoding: 编码
    :return: 当加载成功，返回有元素的dict，否则返回空dict
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return yaml.load(f, yaml.FullLoader)
    except Exception as e:
        print(e)
        return {}


def yaml_writer(path: str, content: dict, encoding: str = 'utf-8') -> bool:
    """用于减少yaml配置文件输出的重复代码

    :param path: 文件输出路径
    :param content: 要写入文件的字典
    :param encoding: 编码，默认为utf-8
    :return: 布尔值
    """
    try:
        content = yaml.dump(content)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(e)
        return False


def json_loader(path: str, encoding: str = 'utf-8') -> dict:
    """用于减少json文件读取的重复代码

    :param path:
    :param encoding:
    :return: 当加载成功，返回有元素的dict，否则返回空dict
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return {}


def json_writer(path: str, content: dict, encoding: str = 'utf-8') -> bool:
    """确保支持导出非ascii字符的json文档

    :param path:
    :param content:
    :param encoding:
    :return:
    """
    try:
        with open(path, 'w', encoding=encoding) as f:
            json.dump(content, f, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        print(e)
        return False


class DriverManagerMock(object):
    def __init__(self, driver_instance):
        self.d = driver_instance

    @property
    def driver(self):
        return self.d
