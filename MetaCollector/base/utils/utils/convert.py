from datetime import datetime
from decimal import Decimal
from typing import Union


def string2number(raw_input: str,
                  output_type: int = 0,
                  output_round: int = 0,
                  is_percentage: bool = False) -> Union[int, float]:
    """将字符串的数字去掉千分位符号，
    并根据output_type决定返回整型还是浮点数，output_round指定输出浮点数时的小数保留位数

    :param raw_input: 原始输入字符串
    :param output_type: int 输出类型，值为0时输出整数，为1时输出浮点数，默认0
    :param output_round: 输出位数的保留小数位数，默认为0
    :param is_percentage: 是否为百分数，是则转换为浮点数
    :return:
    """
    if is_percentage:
        segments_exclude_sep = raw_input.split(',')
        origin_number_in_string = ''.join(segments_exclude_sep)
        raw_deci = Decimal(origin_number_in_string)
        origin_number_in_decimal = raw_deci / Decimal('100')
        return round(float(origin_number_in_decimal), output_round)
    else:
        segments_exclude_sep = raw_input.split(',')
        origin_number_in_string = ''.join(segments_exclude_sep)
        if output_type == 0:
            return int(origin_number_in_string)
        else:
            return round(float(origin_number_in_string), output_round)


def percent_string2num(content: str) -> float:
    """将百分数的字符串转换为浮点数

    :param content: 字符串，格式如854.22%
    :return:
    """
    content_com_rate_percent: str = content.replace("%", "")
    return string2number(content_com_rate_percent, 1, 4, True)


def currency_string2num(content: str, currency_sign: str = None) -> float:
    """将带中文货币符号的的字符串转换为浮点数

    :param content: 字符串，格式为￥23.34
    :param currency_sign: 货币符号，默认值为￥
    :return:
    """
    if currency_sign:
        content_currency: str = content.split(currency_sign)[-1]
    else:
        content_currency: str = content.split("￥")[-1]
    return string2number(content_currency, 1, 2)


def int2date(year: int, month: int, day: int) -> datetime:
    """将多个数值转换合并为日期

    :param year:
    :param month:
    :param day:
    :return:
    """
    return datetime.strptime('{}-{}-{}'.format(year, month, day),
                             '%Y-%m-%d')


def str2date(date_str: str) -> datetime:
    """将日期字符串转换为日期类型

    :param date_str: 日期字符串，格式为year-month-day
    :return: 日期
    """
    return datetime.strptime(date_str, '%Y-%m-%d')


def now2date_str() -> str:
    """将当前时间转换为年月日的字符串

    :return:
    """
    return datetime.now().strftime('%Y-%m-%d')


def now2datetime_str() -> str:
    """将当前时间转换为年月日时分秒的字符串

    :return:
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def timestamp2datetime_str(ts: str) -> str:
    """将时间错字符串转换为年月日时分秒的字符串

    :return:
    """
    ts = int(ts)
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def date2str(dt: datetime) -> str:
    """将YYYY-MM-DD的datetime类型转换为字符串

    :param dt:
    :return:
    """
    return datetime.strftime(dt, '%Y-%m-%d')
