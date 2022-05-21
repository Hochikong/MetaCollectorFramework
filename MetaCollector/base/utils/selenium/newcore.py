import os
from datetime import datetime
from typing import Any

from MetaCollector.base.utils.selenium import check_hide_report


class AbstractCrawler(object):
    def __init__(self,
                 driver_obj: Any,
                 js_path: str,
                 cfg_dict: dict,
                 username: str = None,
                 password: str = None,
                 download_dir: str = None,
                 disable_insert: bool = False,
                 enable_wire: bool = False,
                 enable_uc: bool = False
                 ):
        """基本的构造函数

        :param driver_obj: Chromedriver实例
        :param js_path: stealth.js的路径
        :param cfg_dict: 以字典格式保存的配置内容，可以从json或者yaml读入得到
        :param username: 对应的登陆账户名
        :param password: 对应的账户登陆密码
        :param download_dir: 文件指定的下载目录
        :param disable_insert: 是否禁用传统脚本注入式的浏览器信息隐藏
        :param enable_wire: 是否启用selenium wire
        :param enable_uc: 是否启用undetected chromedriver
        """
        self.download_dir = download_dir
        self.password = password
        self.username = username
        self.config = cfg_dict
        self.brow = driver_obj
        self.stealth_js = js_path
        self.logger = None
        self.disable_insert = disable_insert
        self.use_wire = enable_wire
        self.use_uc = enable_uc

    def safe_check(self, disable_script_insert: bool = False):
        if self.use_wire:
            return
        elif self.use_uc:
            return
        elif self.disable_insert:
            return
        else:
            if disable_script_insert:
                return
            else:
                self.__hide_info()
        # 2021-11-15 停用测试
        # if not self.__hide_passed():
        #     self.logger.error("selenium webdriver隐藏测试不通过，停止取数")
        #     raise AssertionError("Antibots测试失败")

    def safe_check_v2(self):
        # 隐藏浏览器信息通过配置文件设置即可
        self.logger.info('通过配置文件完成隐藏浏览器信息设置')

    @classmethod
    def mini_build(cls, driver_obj, js_path, cfg_dict):
        """最简单的构造函数

        :param driver_obj: Chromedriver实例
        :param js_path: stealth.js的路径
        :param cfg_dict: 以字典格式保存的配置内容，可以从json或者yaml读入得到
        :return:
        """
        return cls(driver_obj=driver_obj, js_path=js_path, cfg_dict=cfg_dict)

    def __hide_info(self):
        # hide selenium info
        with open(self.stealth_js) as jsf:
            js = jsf.read()

        self.brow.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })
        self.logger.info('完成隐藏浏览器信息设置')

    def __hide_passed(self) -> bool:
        self.logger.info("正在测试Antibots")
        if check_hide_report(self.brow, 2):
            self.logger.info('AntiBots测试通过')
            return True
        else:
            self.logger.warning('AntiBots测试未未通过')
            report_file_name = r"{}{}error_{}.html".format(self.config['log']['screenshots'], os.sep,
                                                           datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            with open(report_file_name, 'w') as f:
                f.write(self.brow.page_source)
            self.logger.error("网页报告报告已打印到{}".format(report_file_name))
            return False

    def change_window_size(self, x: int, y: int):
        """更改浏览器窗口的尺寸，以免取不到某些内容

        :param x:
        :param y:
        :return:
        """
        self.brow.set_window_size(x, y)

    def dispose(self, msg=""):
        print(msg)
        self.brow.quit()
