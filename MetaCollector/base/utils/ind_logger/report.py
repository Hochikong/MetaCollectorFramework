# -*- coding: utf-8 -*-
# @Time    : 2022/5/21 20:03
# @Author  : Hochikong
# @FileName: report.py

def beauty_dict_report(data: dict):
    """
    用于美化字典返回一个字符串作为REPL模式的执行报告汇总信息

    :param data:
    :return:
    """
    rows = []
    for k in data.keys():
        tmp = f"{k} -> Status: {data[k][0]}\n    {data[k][-1]}\n\n"
        rows.append(tmp)

    return ''.join(rows)
