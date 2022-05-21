# -*- coding: utf-8 -*-
# @Time    : 2022/5/22 1:44
# @Author  : Hochikong
# @FileName: request_downloader.py

import concurrent.futures
from typing import List

from tqdm import tqdm

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

    def download(self, urls_with_path: List[tuple]):
        """
        给一个list，list包含两个字段：url与目标名字进行下载

        :param urls_with_path: e.g. [('url'http://xxx.jpg', '/PATH_TO/xxx.jpg')]
        :return:
        """
        self.progress = tqdm(total=len(urls_with_path))
        concurrent.futures.wait([self.pool.submit(self.__download, down_dict)
                                 for down_dict in urls_with_path], return_when='ALL_COMPLETED')
        self.progress.close()

    def __download(self, down_dict: tuple):
        data = self.hm.send_request(url=down_dict[0], timeout=self.timeout)
        self.hm.download_file(data.content, down_dict[1])
        self.progress.update(1)
