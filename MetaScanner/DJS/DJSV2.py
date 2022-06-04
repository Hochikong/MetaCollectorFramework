# -*- coding: utf-8 -*-
# @Time    : 2022/3/5 15:34
# @Author  : Hochikong
# @FileName: DJSV2.py

import argparse
import json
import os
import pickle

from MetaCollector.base.utils.db.udao import UniversalDAO
from MetaScanner.DJS.utils import list_median, walk_through_files


class DJSScannerV2(object):
    def __init__(self, scan_path: str, db_url: str, pickle_save_dir: str):
        self.sc_path = scan_path
        self.db_url = db_url
        self.pickle_path = pickle_save_dir

    def scanner(self) -> dict:
        meta_files = []
        for i in walk_through_files(self.sc_path, 'metadata'):
            meta_files.append(i)

        meta_jsons = []
        for f in meta_files:
            with open(f, 'r', encoding='utf-8') as ft:
                meta_jsons.append(json.load(ft))

        main_d = []
        associates = []

        for ind, d in enumerate(meta_jsons):
            p = meta_files[ind].replace(f'{os.sep}metadata.txt', '')
            print(f"Scanning path: {p}")
            main_data = {
                'url': d['URL'],
                'index_title': d['Index Title'],
                'origin_title': d['Origin Title'],
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'pages': int(d['Pages']),
                'uploaded': d['Uploaded'],
                'path': p
            }

            files = [f for f in os.listdir(main_data['path']) if 'metadata' not in f]
            sort_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
            with open(f"{p}{os.sep}{sort_files[0]}", 'rb') as f1:
                main_data['preview'] = f1.read()
            with open(f"{p}{os.sep}{list_median(sort_files)}", 'rb') as f2:
                main_data['secondary_preview'] = f2.read()

            main_d.append(main_data)

            tags = d.get('Tags', [])
            tag_data = None
            for t in tags:
                tag_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Tags',
                    'p_value': t.split("-count:")[0].strip()
                }
            if tag_data is not None:
                associates.append(tag_data)

            artists = d.get('Artists', [])
            artists_data = None
            for a in artists:
                artists_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Artists',
                    'p_value': a.split("-count:")[0].strip()
                }
            if artists_data is not None:
                associates.append(artists_data)

            groups = d.get('Groups', [])
            groups_data = None
            for a in groups:
                groups_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Groups',
                    'p_value': a.split("-count:")[0].strip()
                }
            if groups_data is not None:
                associates.append(groups_data)

            languages = d.get('Languages', [])
            languages_data = None
            for a in languages:
                languages_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Languages',
                    'p_value': a.split("-count:")[0].strip()
                }
            if languages_data is not None:
                associates.append(languages_data)

            categories = d.get('Categories', [])
            categories_data = None
            for a in categories:
                categories_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Categories',
                    'p_value': a.split("-count:")[0].strip()
                }
            if categories_data is not None:
                associates.append(categories_data)

            parodies = d.get('Parodies', [])
            parodies_data = None
            for a in parodies:
                parodies_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Parodies',
                    'p_value': a.split("-count:")[0].strip()
                }
            if parodies_data is not None:
                associates.append(parodies_data)

            characters = d.get('Characters', [])
            characters_data = None
            for a in characters:
                characters_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Characters',
                    'p_value': a.split("-count:")[0].strip()
                }
            if categories_data is not None:
                associates.append(characters_data)
        print("Scan done.")

        return {'djs_books': main_d, 'djs_associate': list(filter(lambda x: x is not None, associates))}

    def save_pickle(self, scanner_input: dict) -> str:
        print("Save data as pickle file")
        save_path = f"{self.pickle_path}{os.sep}djs_scan_temp.dat"
        with open(save_path, "wb") as f:
            pickle.dump(scanner_input, f)

        return save_path

    def import_db(self, scanner_input: dict) -> bool:
        print("Import data to database")
        dao = UniversalDAO(self.db_url)
        dao.custom_import_raise('djs_books', scanner_input['djs_books'])
        dao.custom_import_raise('djs_associate', scanner_input['djs_associate'])
        return True


def scan_cli_launch():
    parser = argparse.ArgumentParser("DJS Scanner V2")
    parser.add_argument('-p', '--path',
                        type=str, help="目标扫描路径", metavar="/PATH/DJS")
    parser.add_argument('--db',
                        type=str, help="适用于sqlalchemy的数据库连接URL", metavar="URL")
    parser.add_argument('--pickle',
                        type=str, help="pickle保存目录", metavar="/PATH/SAVE_PICKLE")
    args = parser.parse_args()
    if args.db and args.pickle:
        djs = DJSScannerV2(args.path, args.db, args.pickle)
        data = djs.scanner()
        djs.save_pickle(data)
        djs.import_db(data)

    elif args.pickle:
        djs = DJSScannerV2(args.path, '', args.pickle)
        data = djs.scanner()
        djs.save_pickle(data)

    elif args.db:
        djs = DJSScannerV2(args.path, args.db, '')
        data = djs.scanner()
        djs.import_db(data)


def append_cli_launch():
    parser = argparse.ArgumentParser("DJS Data Append Tool")
    parser.add_argument('--pickle',
                        type=str, help="用于加载的pickle文件路径", metavar="/PATH/SAVE_PICKLE")
    parser.add_argument('--db',
                        type=str, help="适用于sqlalchemy的数据库连接URL用于数据导入", metavar="URL")
    args = parser.parse_args()
    djs = DJSScannerV2('', args.db, args.pickle)
    with open(args.pickle, 'rb') as f:
        data = pickle.load(f)
    djs.import_db(data)


if __name__ == '__main__':
    scan_path = r"F:\manga"
    url = r'sqlite:///C:\Users\ckhoi\PycharmProjects\MetaCollectorFramework\djs.db'
