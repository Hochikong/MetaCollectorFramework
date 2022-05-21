import base64
import time

import cv2
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains

from MetaCollector.base.utils.random import EasingUtils, uniform
from MetaCollector.base.utils.random import generate_random_float


def get_pull_distance(background_pic: str, small_pic: str, enable_scaling: bool = False, scaling: float = 0.0) -> int:
    """通过OpenCV计算拼图的目标所需移动的距离

    :param background_pic: 背景图的路径
    :param small_pic: 小拼图的路径
    :param enable_scaling: 是否启用缩放
    :param scaling: 缩放比例，如京东的为278/360（网页上图片尺寸比真实图片尺寸小，网页上宽度大概为278，真实宽度为360）
    :return: 拖动距离
    """
    background_template = cv2.imread(background_pic, cv2.IMREAD_GRAYSCALE)
    small_picture = cv2.imread(small_pic, cv2.IMREAD_GRAYSCALE)

    res = cv2.matchTemplate(background_template, small_picture, cv2.TM_CCORR_NORMED)
    value = cv2.minMaxLoc(res)[2][0]

    if enable_scaling:
        distance = value * scaling
        return distance
    else:
        return value


def refresh_pics(driver: Chrome, background_xpath: str, small_pic_xpath: str):
    """下载最新的拼图png文件，包含背景大图和小拼图两张图片

    :param driver: selenium.webdriver.Chrome对象实例
    :param background_xpath: 背景图的Xpath
    :param small_pic_xpath: 小拼图的Xpath
    :return:
    """
    img_bg_src = driver.find_element_by_xpath(background_xpath).get_attribute(
        'src')
    # base64解码保存
    with open('bg.png', 'wb') as fi:
        fi.write(base64.b64decode(img_bg_src.split(',')[1]))

    # 获取小图
    img_sm_src = driver.find_element_by_xpath(small_pic_xpath).get_attribute('src')
    with open('sm.png', 'wb') as fi:
        fi.write(base64.b64decode(img_sm_src.split(',')[1]))


class UnexpectElementAppear(Exception):
    pass


def puzzle_hammer(driver: Chrome,
                  max_retry: int,
                  expect_elements: list,
                  unexpect_elements: list,
                  background_xpath: str,
                  small_pic_xpath: str,
                  slide_btn_xpath: str,
                  moe: float = round(uniform(0.0, 0.6), 2)
                  ) -> bool:
    """拼图验证码破门锤
    传入一个Chrome实例对象和一些xpath，在检测到expect_element_xpath之前都会反复重试破门而入搞掉拼图

    :param driver: Chrome实例
    :param max_retry: 最大重试次数
    :param expect_elements: 门后的目标列表，当检测到当中的任意元素之后就会停止破门
    :param unexpect_elements: 意外的元素列表，正常破门后不应该出现
    :param background_xpath: 背景图的xpath
    :param small_pic_xpath: 小拼图的xpath
    :param slide_btn_xpath: 滑动按钮的xpath
    :param moe: margin of error, 误差幅度，一般该值不要超过1，默认值在0到0.6之间，保留两位小数
    :return:
    """
    retry_times = 0
    result = False

    for i in range(max_retry):
        # 超过重试次数
        if retry_times > max_retry:
            break
        else:
            need_continue = True
            retry_times += 1
            try:
                refresh_pics(driver, background_xpath, small_pic_xpath)

                offset = get_pull_distance('bg.png', 'sm.png', True, (278 / 360)) + round(moe, 2)
                offsets, tracks = EasingUtils.get_tracks(offset, 1, 'expo')
                tracks.append(tracks[-1] + 2)
                tracks.append(tracks[-1] - 2)

                slide_btn = driver.find_element_by_xpath(
                    slide_btn_xpath)

                ActionChains(driver).click_and_hold(slide_btn).perform()
                for x in tracks:
                    ActionChains(driver).move_by_offset(x, 0).perform()
                ActionChains(driver).pause(0.2).release().perform()

                time.sleep(5)
            # when login actually passed
            except NoSuchElementException:
                print('已无拼图')
                time.sleep(3)
                ec = len(expect_elements)
                for ele in expect_elements:
                    try:
                        if driver.find_element_by_xpath(ele):
                            print('找到一个目标元素，停止重试')
                            break
                        else:
                            for xp in unexpect_elements:
                                if driver.find_element_by_xpath(xp):
                                    raise UnexpectElementAppear("出现意外元素。停止破门")
                    except NoSuchElementException:
                        ec -= 1

                if ec > 0:
                    need_continue = False
                else:
                    need_continue = True

            if need_continue:
                time.sleep(generate_random_float(3, 7))
                continue
            else:
                result = True
                break

    return result
