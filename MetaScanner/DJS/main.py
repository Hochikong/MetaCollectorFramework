# -*- coding: utf-8 -*-
# @Time    : 2022/6/19 18:53
# @Author  : Hochikong
# @FileName: main.py
import argparse
import pickle

from MetaScanner.DJS.DJSV1 import DJSScannerV1
from MetaScanner.DJS.DJSV2 import DJSScannerV2


def scan_cli_launch():
    parser = argparse.ArgumentParser("DJS Scanner V2")
    parser.add_argument('-p', '--path',
                        type=str, help="目标扫描路径", metavar="/PATH/DJS")
    parser.add_argument('--db',
                        type=str, help="适用于sqlalchemy的数据库连接URL", metavar="URL")
    parser.add_argument('--tag',
                        type=str, help="设备标签", metavar="用于标识数据所在设备的自定义tag")
    parser.add_argument('--pickle',
                        type=str, help="pickle保存目录", metavar="/PATH/SAVE_PICKLE")
    parser.add_argument('--version',
                        type=str, help="元数据版本", metavar="V2 或 V1")

    args = parser.parse_args()
    if args.db and args.pickle:
        if args.version.strip() == 'V1':
            djs = DJSScannerV1(args.path, args.db, args.pickle)
        elif args.version.strip() == 'V2':
            djs = DJSScannerV2(args.path, args.db, args.pickle)
        else:
            raise NotImplementedError("不支持的元数据版本参数")
        data = djs.scanner(args.tag)
        djs.save_pickle(data)
        djs.import_db(data)

    elif args.pickle:
        if args.version.strip() == 'V1':
            djs = DJSScannerV1(args.path, '', args.pickle)
        elif args.version.strip() == 'V2':
            djs = DJSScannerV2(args.path, '', args.pickle)
        else:
            raise NotImplementedError("不支持的元数据版本参数")
        data = djs.scanner(args.tag)
        djs.save_pickle(data)

    elif args.db:
        if args.version.strip() == 'V1':
            djs = DJSScannerV1(args.path, args.db, '')
        elif args.version.strip() == 'V2':
            djs = DJSScannerV2(args.path, args.db, '')
        else:
            raise NotImplementedError("不支持的元数据版本参数")

        data = djs.scanner(args.tag)
        djs.import_db(data)


def append_cli_launch():
    parser = argparse.ArgumentParser("DJS Data Append Tool")
    parser.add_argument('--pickle',
                        type=str, help="用于加载的pickle文件路径", metavar="/PATH/SAVE_PICKLE")
    parser.add_argument('--db',
                        type=str, help="适用于sqlalchemy的数据库连接URL用于数据导入", metavar="URL")
    parser.add_argument('--version',
                        type=str, help="元数据版本", metavar="V2 或 V1")
    args = parser.parse_args()
    if args.version.strip() == 'V1':
        djs = DJSScannerV1('', args.db, args.pickle)
    elif args.version.strip() == 'V2':
        djs = DJSScannerV2('', args.db, args.pickle)
    else:
        raise NotImplementedError("不支持的元数据版本参数")

    with open(args.pickle, 'rb') as f:
        data = pickle.load(f)
    djs.import_db(data)
