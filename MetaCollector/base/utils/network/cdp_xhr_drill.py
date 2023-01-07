# -*- coding: utf-8 -*-
# @Time    : 2023/1/7 23:37
# @Author  : Hochikong
# @FileName: cdp_xhr_drill.py
import json
import time
from typing import Any

from selenium.webdriver import Chrome


class CDPXHRDrill(object):
    def __init__(self, driver: Chrome, wait_version: str = 'latest'):
        self.brow = driver
        self.request_url_id = {}
        self._wait_version = wait_version if wait_version in ('latest', 'legacy', 'V3') else 'legacy'

    def clean_cdp_logs(self):
        self.request_url_id = {}
        self.brow.execute_cdp_cmd('Log.clear', {})
        time.sleep(1)

    @staticmethod
    def log_filter(log_: list):
        # is an actual response and json
        return log_["method"] == "Network.responseReceived" and "json" in log_["params"]["response"]["mimeType"]

    def wait_for_request_V1(self, url_seg: str) -> Any:
        """
        获取除了已经取过的请求以外最早的请求

        :param url_seg:
        :return:
        """
        logs_raw = self.brow.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

        for log in filter(CDPXHRDrill.log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            if url_seg in resp_url and float(request_id) > self.request_url_id.get(url_seg, 0):
                self.request_url_id[url_seg] = float(request_id)
                try:
                    return self.brow.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                except Exception as e:
                    # raise RuntimeError(f"Get Response Body Error: {e}")
                    pass
        return None

    def wait_for_request_V2(self, url_seg: str, max_try: int = 20) -> Any:
        """
        只获取最新的请求(只要响应)

        :param url_seg:
        :param max_try: 等待请求完成前的重试次数
        :return:
        """
        max_try_count = max_try
        while max_try_count > 0:
            max_try_count -= 1
            logs_raw = self.brow.get_log("performance")
            logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

            req_ids = []
            for log in filter(CDPXHRDrill.log_filter, logs):
                request_id = log["params"]["requestId"]
                resp_url = log["params"]["response"]["url"]
                if url_seg in resp_url:
                    req_ids.append(request_id)

            try:
                self.request_url_id[url_seg] = float(req_ids[-1])
                return self.brow.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_ids[-1]})
            except Exception as e:
                # raise RuntimeError(f"Get Response Body Error: {e}")
                time.sleep(1)
                continue

        return None

    def wait_for_request_V3(self, url_seg: str, max_try: int = 20) -> Any:
        """
        只获取最新的请求(包含请求体)

        :param url_seg:
        :param max_try: 等待请求完成前的重试次数
        :return:
        """
        max_try_count = max_try
        while max_try_count > 0:
            max_try_count -= 1
            logs_raw = self.brow.get_log("performance")
            logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

            req_ids = []
            for log in filter(CDPXHRDrill.log_filter, logs):
                request_id = log["params"]["requestId"]
                resp_url = log["params"]["response"]["url"]
                if url_seg in resp_url:
                    req_ids.append(request_id)

            xhr = {}
            try:
                # self.request_url_id[url_seg] = float(req_ids[-1])
                # return self.brow.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_ids[-1]})
                self.request_url_id[url_seg] = float(req_ids[-1])
                xhr['response'] = self.brow.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_ids[-1]})
                xhr['body'] = self.brow.execute_cdp_cmd("Network.getRequestPostData", {"requestId": req_ids[-1]})
                return xhr
            except Exception as e:
                # raise RuntimeError(f"Get Response Body Error: {e}")
                time.sleep(1)
                continue

        return None

    def wait_for_request(self, url_seg: str, max_try: int = 20) -> Any:
        if self._wait_version == 'legacy':
            return self.wait_for_request_V1(url_seg)
        if self._wait_version == 'latest':
            return self.wait_for_request_V2(url_seg, max_try)
        if self._wait_version == 'V3':
            return self.wait_for_request_V3(url_seg, max_try)
        return None


class CDPXHRDrillTool(object):
    @staticmethod
    def wait_for_request(driver, url_seg: str, max_try: int = 20) -> Any:
        drill = CDPXHRDrill(driver)
        return drill.wait_for_request(url_seg, max_try)
