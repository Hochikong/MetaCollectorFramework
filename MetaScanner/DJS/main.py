# -*- coding: utf-8 -*-
# @Time    : 2022/6/19 18:53
# @Author  : Hochikong
# @FileName: main.py
import argparse
import pickle

from MetaScanner.DJS.DJSV1 import DJSScannerV1
from MetaScanner.DJS.DJSV2 import DJSScannerV2
from MetaScanner.DJS.utils import SQLiteMetadataRepoUtil, djs_books_sqlite_to_parquet


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


def init_new_metadata_db():
    parser = argparse.ArgumentParser("Init new metadata db")
    parser.add_argument('-p', '--path',
                        type=str, help="目标路径", metavar="/PATH/DJS.db")

    args = parser.parse_args()
    ru = SQLiteMetadataRepoUtil(args.path)
    ru.init_new_db()
    print(f"sqlite:///{args.path}")


def sqlite2parquet():
    parser = argparse.ArgumentParser("SQLite to parquet file")
    parser.add_argument('-p', '--path',
                        type=str, help="目标路径", metavar="/PATH/DJS.db", required=True)
    parser.add_argument('-t', '--table',
                        type=str, help="表名", metavar="TABLE_NAME", required=True)
    parser.add_argument('-o', '--output',
                        type=str, help="输出路径", metavar="/PATH/xxx.parquet")

    args = parser.parse_args()
    out = djs_books_sqlite_to_parquet(args.path, args.table, args.output)
    print(f"parquet file saved to {out}")

# Usage
# 导入数据
# djs_scan -p \\DESKTOP-INTEL31\XXX --db sqlite:///G:\MetaDataCenter\TMP\djs.db --tag intel_laptop --version V1
#
# djs_scan -p \\DESKTOP-INTEL31\Doujinshis\ --db sqlite:///G:\MetaDataCenter\djs.db --tag intel_laptop --version V2

# 新数据库
# new_djs_db -p G:\\TMP\\DJS.db
