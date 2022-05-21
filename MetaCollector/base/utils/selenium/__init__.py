import time

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome


def check_hide_report(driver: Chrome, tolerance: int) -> bool:
    """检查是否通过了antibot测试

    :param driver: Chrome实例
    :param tolerance: 容忍度，容忍有多少项测试不通过
    :return: 简单判断是否通过测试
    """
    CHECK_URL = 'https://bot.sannysoft.com/'
    TESTS_COUNT = 12

    driver.get(CHECK_URL)
    time.sleep(5)
    driver.save_screenshot('antibot_report.png')
    print("已导出检测截图")

    html = BeautifulSoup(driver.page_source, 'lxml')
    tables = html.find_all('table')
    first_table = tables[0]
    trs = first_table.find_all('tr')
    passwd_count = [tr.find(class_='passed') for tr in trs]
    print("通过了{}项测试".format(len(passwd_count)))
    if len(passwd_count) >= (TESTS_COUNT - tolerance):
        return True
    else:
        return False
