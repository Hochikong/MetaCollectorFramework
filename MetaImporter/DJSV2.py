# -*- coding: utf-8 -*-
# @Time    : 2022/3/5 15:34
# @Author  : Hochikong
# @FileName: DJSV2.py

import json
import os
from typing import List

from sqlalchemy import Table, MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# connection = sqlite3.connect("hentai.db")

scan_path = r"F:\djs\manga"
url = r'sqlite:///C:\Users\ckhoi\PycharmProjects\PlayGround\djs.db'


class UniversalDAO(object):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.md = None
        self.engine = None
        self.session: Session = None
        self.table_object: Table = None

    def _connect(self):
        try:
            self.session.close()
        except Exception:
            pass
        self.md = MetaData()
        self.engine = create_engine(self.db_url)
        self.session = Session(self.engine)

    def _disconnect(self):
        self.session.close()

    def custom_import(self, table: str, data: List[dict]) -> bool:
        return self.__import(data, table)

    def custom_import_raise(self, table: str, data: List[dict]) -> bool:
        """
        会抛出RuntimeError异常的导入函数，方便实现原子操作

        :param table:
        :param data:
        :return:
        """
        em = None
        self._connect()
        self.table_object = Table(table, self.md, autoload=True, autoload_with=self.engine)
        succeed = 0
        try:
            self.session.execute(self.table_object.insert(), data)
            self.session.commit()
            succeed = 1
        except Exception as e:
            em = str(e)
            self.session.rollback()
            succeed = 0
        finally:
            self._disconnect()
            if succeed == 1:
                return True
            else:
                raise RuntimeError("导入报错: \n{}".format(em))

    def __import(self, data, table_name):
        self._connect()
        self.table_object = Table(table_name, self.md, autoload=True, autoload_with=self.engine)
        succeed = 0
        try:
            self.session.execute(self.table_object.insert(), data)
            self.session.commit()
            succeed = 1
        except Exception as e:
            print("报错：{}".format(e))
            self.session.rollback()
            succeed = 0
        finally:
            self._disconnect()
            return succeed == 1


def walk_through_files(path, startswith):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.startswith(startswith):
                yield os.path.join(dirpath, filename)


if __name__ == '__main__':
    meta_files = []
    for i in walk_through_files(scan_path, 'metadata'):
        meta_files.append(i)

    meta_jsons = []
    for f in meta_files:
        with open(f, 'r', encoding='utf-8') as ft:
            meta_jsons.append(json.load(ft))

    dao = UniversalDAO(url)

    main_d = []
    associates = []

    for ind, d in enumerate(meta_jsons):
        main_data = {
            'url': d['URL'],
            'index_title': d['Index Title'],
            'origin_title': d['Origin Title'],
            'gallery_id': int(d['Gallery ID'].replace("#", '')),
            'pages': int(d['Pages']),
            'uploaded': d['Uploaded'],
            'path': meta_files[ind].replace(f'{os.sep}metadata.txt', '')
        }
        main_d.append(main_data)

        tags = d.get('Tags', [])
        for t in tags:
            tag_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Tags',
                'p_value': t.split("-count:")[0].strip()
            }
            associates.append(tag_data)

        artists = d.get('Artists', [])
        for a in artists:
            artists_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Artists',
                'p_value': a.split("-count:")[0].strip()
            }
            associates.append(artists_data)

        groups = d.get('Groups', [])
        for a in groups:
            groups_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Groups',
                'p_value': a.split("-count:")[0].strip()
            }
            associates.append(groups_data)

        languages = d.get('Languages', [])
        for a in languages:
            languages_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Languages',
                'p_value': a.split("-count:")[0].strip()
            }
            associates.append(languages_data)

        categories = d.get('Categories', [])
        for a in categories:
            categories_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Categories',
                'p_value': a.split("-count:")[0].strip()
            }
            associates.append(categories_data)

        parodies = d.get('Parodies', [])
        for a in parodies:
            parodies_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Parodies',
                'p_value': a.split("-count:")[0].strip()
            }
            associates.append(parodies_data)

        characters = d.get('Characters', [])
        for a in parodies:
            characters_data = {
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'property': 'Characters',
                'p_value': a.split("-count:")[0].strip()
            }
            associates.append(characters_data)

    dao.custom_import('hentai_books', main_d)
    dao.custom_import('hentai_associate', associates)
