# -*- coding: utf-8 -*-
# @Time    : 2022/6/4 22:41
# @Author  : Hochikong
# @FileName: utils.py
import io
import math
import os
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image
from sqlalchemy import Table

from MetaCollector.base.utils.db.udao import UniversalDAO


def list_median(list_):
    middle = math.trunc(len(list_) / 2)
    return list_[middle]


def walk_through_files(path, startswith):
    for (dir_path, dir_names, filenames) in os.walk(path):
        for filename in filenames:
            if filename.startswith(startswith):
                yield os.path.join(dir_path, filename)


class SQLiteMetadataRepoUtil(object):
    def __init__(self, db_file: str = None):
        self.dat_path = db_file

        self.__drop = """
                      DROP TABLE IF EXISTS djs_books;

                      DROP TABLE IF EXISTS djs_associate; \
                      """

        self.__ddl = """
                     create table djs_books
                     (
                         id                integer primary key autoincrement,
                         url               text(500) not null,
                         index_title       text(500) not null,
                         origin_title      text(500) not null,
                         gallery_id        integer not null,
                         pages             integer not null,
                         uploaded          text(100) not null,
                         path              text(500) not null unique,
                         device_tag        text(100) not null default '',
                         meta_version      text(10)  not null,
                         preview           BLOB,
                         secondary_preview BLOB
                     );

                     create table djs_associate
                     (
                         id         integer primary key autoincrement,
                         gallery_id integer not null,
                         property   text(10) not null,
                         p_value    text(50) not null
                     ); \
                     """

        self.__truncate = """
                          DELETE
                          FROM djs_books;

                          DELETE
                          FROM sqlite_sequence
                          WHERE name = 'djs_books';

                          DELETE
                          FROM djs_associate;

                          DELETE
                          FROM sqlite_sequence
                          WHERE name = 'djs_associate'; \
                          """

    def init_new_db(self, target_file: str = None) -> str:
        if not target_file:
            target_file = self.dat_path
        connection = sqlite3.connect(target_file)

        # create table
        cursor_obj = connection.cursor()
        cursor_obj.executescript(self.__drop)
        cursor_obj.executescript(self.__ddl)
        cursor_obj.close()

        connection.close()
        return target_file

    def truncate_data(self, target_file: str = None):
        if not target_file:
            target_file = self.dat_path
        connection = sqlite3.connect(target_file)

        cursor_obj = connection.cursor()
        cursor_obj.executescript(self.__truncate)
        connection.close()

        return True


class SimpleDJSQueryDAO(UniversalDAO):
    def __init__(self, db_url: str):
        super(SimpleDJSQueryDAO, self).__init__(db_url)

    def save_preview(self, id_: int, path: str):
        self._connect()
        table_object = Table('djs_books', self.md, autoload=True, autoload_with=self.engine)
        r = self.session.query(table_object).filter_by(id=id_).all()
        preview = r[0]._asdict()['preview']
        self._disconnect()
        image = Image.open(io.BytesIO(preview))
        image.save(path)
        return path


def djs_books_sqlite_to_parquet(db_path: str,
                      table: str = "djs_books",
                      output: Optional[str] = None,
                      **kwargs) -> Path:
    """
    将 SQLite 中的指定表导出为 parquet 文件。
    参数
    ----
    db_path : str | Path
        SQLite 文件路径
    table : str, 默认 "prefilter_data"
        要导出的表名
    output : str | Path | None, 可选
        输出 parquet 文件路径。若为 None，则自动生成：
        <db_path所在目录>/<table>.parquet
    **kwargs :
        透传给 pandas.to_parquet 的额外参数，如 compression='snappy'
    返回
    ----
    Path
        生成的 parquet 文件路径
    """
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite 文件不存在: {db_path}")
    # 自动命名输出文件
    if output is None:
        output = db_path.with_name(f"{table}.parquet")
    else:
        output = Path(output)
    # 连接数据库并一次性读取
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

    df['preview'] = None
    df['secondary_preview'] = None
    # 写入 parquet
    df.to_parquet(output, **kwargs)
    return output

# if __name__ == '__main__':
#     ru = SQLiteMetadataRepoUtil(r'C:\Users\ckhoi\PycharmProjects\MetaCollectorFramework\djs.db')
#     ru.init_new_db()

# 导入数据
# djs_scan -p \\DESKTOP-INTEL31\XXX --db sqlite:///G:\MetaDataCenter\TMP\djs.db --tag intel_laptop --version V1
#
# djs_scan -p \\DESKTOP-INTEL31\Doujinshis\ --db sqlite:///G:\MetaDataCenter\djs.db --tag intel_laptop --version V2

# 新数据库
# new_djs_db -p G:\\TMP\\DJS.db
