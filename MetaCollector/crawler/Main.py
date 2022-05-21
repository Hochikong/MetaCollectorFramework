from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait as Wait

from MetaCollector.base.utils.ind_logger import logger, add_logger_config
from MetaCollector.base.utils.selenium.newcore import AbstractCrawler


class MCFDataCollector(AbstractCrawler):
    """
    MetaCollectorFramework模块化取数主程序

    """

    def __init__(self,
                 driver_obj: Chrome,
                 js_path: str,
                 cfg_dict: dict,
                 username: str = None,
                 password: str = None,
                 download_dir: str = None,
                 disable_insert: bool = False,
                 enable_wire: bool = False,
                 enable_uc: bool = False):
        super(MCFDataCollector, self).__init__(
            driver_obj=driver_obj,
            js_path=js_path,
            cfg_dict=cfg_dict,
            username=username,
            password=password,
            download_dir=download_dir,
            disable_insert=disable_insert,
            enable_wire=enable_wire,
            enable_uc=enable_uc
        )

        self.logger = logger

        log_path = 'logs/mcf_log'
        if cfg_dict['log'].get('logfile_prefix', None):
            log_path = cfg_dict['log']['logfile_prefix']

        self.sink_id = add_logger_config(
            log_path, 'DEBUG', __name__,
            '[{time:YYYY-MM-DD} {time:HH:mm:ss}][{file}.{function}:{line}][{level}] -> {message}'
        )

        self.target_url = ''
        self.wait = Wait(self.brow, 10)
        self.long_wait = Wait(self.brow, 40)

        if not enable_uc:
            self.safe_check(disable_script_insert=True)
        # self.safe_check_v2()

        self.account_status = 'logout'

        # 用于被worker读取的备注
        self.worker_noted = ''

    @classmethod
    def build(cls, driver_obj, cfg_dict, disable_insert, enable_wire, enable_uc):
        return cls(
            driver_obj=driver_obj,
            js_path=cfg_dict['selenium']['stealth_path'],
            cfg_dict=cfg_dict,
            username=cfg_dict['account']['username'],
            password=cfg_dict['account']['password'],
            download_dir=cfg_dict['selenium']['prefs']['download.default_directory'],
            disable_insert=disable_insert,
            enable_wire=enable_wire,
            enable_uc=enable_uc
        )

    def logout(self):
        pass

    def login(self):
        pass

    def log_info(self, msg):
        self.logger.info(msg)

    def log_warning(self, msg):
        self.logger.warning(msg)

    def log_error(self, msg):
        self.logger.error(msg)
