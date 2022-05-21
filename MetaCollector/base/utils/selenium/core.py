import os
from datetime import datetime

from selenium.webdriver import Chrome

from MetaCollector.base.utils.selenium import check_hide_report


class AbstractCrawler(object):
    def __init__(self,
                 driver_obj: Chrome,
                 js_path: str,
                 cfg_dict: dict,
                 logger_: any,
                 username: str = None,
                 password: str = None,
                 download_dir: str = None,
                 ):
        """基本的构造函数

        :param driver_obj: Chromedriver实例
        :param js_path: stealth.js的路径
        :param cfg_dict: 以字典格式保存的配置内容，可以从json或者yaml读入得到
        :param logger_: 支持标准方法的logger实例，如python自带的logging的getLogger，或者loguru等第三方库的logger
        :param username: 对应的登陆账户名
        :param password: 对应的账户登陆密码
        :param download_dir: 文件指定的下载目录
        """
        self.download_dir = download_dir
        self.password = password
        self.username = username
        self.config = cfg_dict
        self.logger = logger_
        self.brow = driver_obj
        self.stealth_js = js_path

        self.__hide_info()
        if not self.__hide_passed():
            self.logger.error("selenium webdriver隐藏测试不通过，停止取数")
            raise AssertionError("Antibots测试失败")

    @classmethod
    def mini_build(cls, driver_obj, js_path, cfg_dict, logger_):
        """最简单的构造函数

        :param driver_obj: Chromedriver实例
        :param js_path: stealth.js的路径
        :param cfg_dict: 以字典格式保存的配置内容，可以从json或者yaml读入得到
        :param logger_: 支持标准方法的logger实例，如python自带的logging的getLogger，或者loguru等第三方库的logger
        :return:
        """
        return cls(driver_obj=driver_obj, js_path=js_path, cfg_dict=cfg_dict, logger_=logger_)

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
