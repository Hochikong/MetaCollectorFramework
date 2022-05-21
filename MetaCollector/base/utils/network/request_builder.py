# -*- coding: utf-8 -*-
# @Time    : 2022/5/21 19:11
# @Author  : Hochikong
# @FileName: request_builder.py
import requests
import urllib3
from requests import exceptions


class HttpRequestsMaker:
    def __init__(self, **kwargs):

        urllib3.disable_warnings()
        self.session = requests.session()
        if "proxies" in kwargs.keys():
            print("proxies:%s" % kwargs.get("proxies"))
            px: dict = kwargs.get("proxies")
            self.session.proxies = px
        if "headers" in kwargs.keys():
            # just add cookie in headers['cookie']
            print("headers:%s" % kwargs.get("headers"))
            hd: dict = kwargs.get("headers")
            self.session.headers.update(hd)

    def send_request(self, method='get', url='', timeout=60, headers=None, data=None, params=None):
        """
        根据拼装的url和请求方法以及各种参数发起一个请求
        """
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        try:
            # return self.session.request(method, self.build_url(url_path),
            # verify=False, *args, **kwargs)
            return self.session.request(method, url, verify=False, headers=headers, data=data, params=params,
                                        timeout=timeout)

        except exceptions.ConnectTimeout as timeout:
            raise timeout
        except exceptions.InvalidURL as invalid_url:
            raise invalid_url
        except exceptions.ProxyError as proxy:
            raise proxy
        except exceptions.ConnectionError as connect_error:
            raise connect_error

    @staticmethod
    def save_html(response_text, file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(response_text)

    @staticmethod
    def download_file(response_content, file_name):
        with open(file_name, "wb") as f:
            f.write(response_content)

    @staticmethod
    def simple_get(url='', headers=None, proxies=None, timeout=30):
        if headers and proxies:
            res = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        elif headers:
            res = requests.get(url, headers=headers, timeout=timeout)
        elif proxies:
            res = requests.get(url, proxies=proxies, timeout=timeout)
        else:
            res = requests.get(url, timeout=timeout)
        if res and res.status_code == 200:
            return res
        else:
            return None

    def quit(self):
        self.__del()

    def __del(self):
        self.session.close()
