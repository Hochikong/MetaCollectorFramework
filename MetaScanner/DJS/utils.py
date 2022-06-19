# -*- coding: utf-8 -*-
# @Time    : 2022/6/4 22:41
# @Author  : Hochikong
# @FileName: utils.py
import io
import math
import os
import sqlite3

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
            
            DROP TABLE IF EXISTS djs_associate;
        """

        self.__ddl = """
        create table djs_books
        (
        id                integer primary key autoincrement,
        url               text(500) not null,
        index_title       text(500) not null,
        origin_title      text(500) not null,
        gallery_id        integer   not null,
        pages             integer   not null,
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
            gallery_id integer  not null,
            property   text(10) not null,
            p_value    text(50) not null
        );
        """

        self.__truncate = """
        DELETE FROM djs_books;
        
        DELETE
        FROM sqlite_sequence
        WHERE name = 'djs_books';
        
        DELETE FROM djs_associate;
        
        DELETE
        FROM sqlite_sequence
        WHERE name = 'djs_associate';
        """

    def init_new_db(self, target_file: str = None) -> str:
        if not target_file:
            target_file = self.dat_path
        connection = sqlite3.connect(target_file)

        # create table
        cursor_obj = connection.cursor()
        cursor_obj.executescript(self.__drop)
        cursor_obj.executescript(self.__ddl)

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

# if __name__ == '__main__':
#     ru = SQLiteMetadataRepoUtil(r'C:\Users\ckhoi\PycharmProjects\MetaCollectorFramework\djs.db')
#     ru.init_new_db()
