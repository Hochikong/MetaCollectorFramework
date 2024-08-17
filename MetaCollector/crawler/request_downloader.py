# -*- coding: utf-8 -*-
# @Time    : 2022/5/22 1:44
# @Author  : Hochikong
# @FileName: request_downloader.py

import concurrent.futures
import time
from typing import List

from tqdm import tqdm
from MetaCollector.base.utils.random import generate_random_float
from MetaCollector.base.utils.network.request_builder import HttpRequestsMaker


class RequestDownloader(object):
    def __init__(self, headers: dict, proxies: dict = None, max_threads: int = 4, max_timeout: int = 30):
        if proxies:
            self.hm = HttpRequestsMaker(headers=headers, proxies=proxies)
        else:
            self.hm = HttpRequestsMaker(headers=headers)
        self.progress = None
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
        self.timeout = max_timeout

    def download(self, urls_with_path: List[tuple], sleep_in_seconds: tuple = None):
        """
        给一个list，list包含两个字段：url与目标名字进行下载

        :param urls_with_path: e.g. [('url'http://xxx.jpg', '/PATH_TO/xxx.jpg')]
        :param sleep_in_seconds: 每下载一个文件的睡眠时间，例如：(1,3)，随机睡眠1~3秒
        :return:
        """
        self.progress = tqdm(total=len(urls_with_path))
        concurrent.futures.wait([self.pool.submit(self.__download, down_dict, sleep_in_seconds)
                                 for down_dict in urls_with_path], return_when='ALL_COMPLETED')
        self.progress.close()

    def __download(self, down_dict: tuple, sleep_in_seconds: tuple = None):
        data = self.hm.send_request(url=down_dict[0], timeout=self.timeout)
        self.hm.download_file(data.content, down_dict[1])
        if sleep_in_seconds is not None:
            t = generate_random_float(sleep_in_seconds[0], sleep_in_seconds[1])
            time.sleep(t)
        self.progress.update(1)
