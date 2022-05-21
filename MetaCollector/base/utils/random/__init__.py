import string
from random import randrange, uniform, choices
from typing import List, Tuple

import numpy as np


def generate_random_str(size: int) -> str:
    """
    生成指定长度的随机字符串

    :param size:
    :return:
    """
    return ''.join(choices(string.ascii_lowercase + string.digits, k=size))


def generate_random_seq(content: str) -> List[str]:
    """对一个字符串返回随机分割的三段

    :param content: 输入的字符串
    :return: 包含原始字符串的所有内容的长度为3的列表
    """
    input_length: int = len(content)
    output: List[str] = []

    # 当输入文本太短时直接返回
    if input_length < 6:
        return [content]

    try:
        random_val = randrange(3, input_length)
        tmp_output = [content[:random_val], content[random_val:]]
        small_one = min(tmp_output)
        max_one = max(tmp_output)

        if max_one == tmp_output[0]:
            random_val = randrange(2, input_length - len(small_one))
            output += [max_one[:random_val], max_one[random_val:]]
            output.append(small_one)
            return output
        else:
            # 当较短的字符串在前面
            output.append(small_one)
            random_val = randrange(2, input_length - len(output[-1]))
            output += [max_one[:random_val], max_one[random_val:]]
            return output

    except ValueError:
        return [content]


def generate_random_float(min_sec: int, max_sec: int) -> float:
    """生成1位小数的随机的睡眠时间

    :param min_sec: 最短睡眠时间
    :param max_sec: 最长睡眠时间
    :return: 返回一个浮点数作为睡眠时间，提供给time.sleep使用
    """
    random_value = uniform(min_sec, max_sec)
    return round(random_value, 1)


class EasingUtils:
    """缓动函数工具类
    主要包含三种近似的缓动函数
    """

    @staticmethod
    def ease_out_expo(distance: int) -> float:
        """ 参考：https://www.xuanfengge.com/easeing/easeing/#easeOutExpo

        :param distance: 拖动距离
        :return:
        """
        if distance == 1:
            return 1
        else:
            return 1 - pow(2, -10 * distance)

    @staticmethod
    def ease_out_quart(distance: int) -> float:
        """参考：https://www.xuanfengge.com/easeing/easeing/#easeOutQuart

        :param distance: 拖动距离
        :return:
        """
        return 1 - pow(1 - distance, 4)

    @staticmethod
    def ease_out_quad(distance: int) -> float:
        """参考：https://www.xuanfengge.com/easeing/easeing/#easeOutQuad

        :param distance: 拖动距离
        :return:
        """
        return 1 - (1 - distance) * (1 - distance)

    @staticmethod
    def get_tracks(distance: float, seconds: int, ease_type: str) -> Tuple[List, List]:
        """根据缓动函数类型，计算ActionChains的运动方式

        :param distance: 拼图拉动距离，用OpenCV计算可得
        :param seconds: 秒数，要求ActionChains必须在该时间内移动到到指定位置
        :param ease_type: 缓动函数类型，目前可选 -> 'expo', 'quart', 'quad'
        :return: 分别返回offsets和tracks
        """
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            if ease_type == 'expo':
                offset = round(EasingUtils.ease_out_expo(t / seconds) * distance)
            elif ease_type == 'quart':
                offset = round(EasingUtils.ease_out_quart(t / seconds) * distance)
            elif ease_type == 'quad':
                offset = round(EasingUtils.ease_out_quad(t / seconds) * distance)
            else:
                offset = round(EasingUtils.ease_out_expo(t / seconds) * distance)

            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        return offsets, tracks
