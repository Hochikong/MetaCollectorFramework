# -*- coding: utf-8 -*-
# @Time    : 2022/3/5 15:34
# @Author  : Hochikong
# @FileName: DJSV2.py

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

    def scanner(self, tag: str) -> dict:
        meta_files = []
        for i in walk_through_files(self.sc_path, 'metadata'):
            meta_files.append(i)

        meta_jsons = []
        for f in meta_files:
            print(f"扫描元数据文件: {f}")
            with open(f, 'r', encoding='utf-8') as ft:
                meta_jsons.append(json.load(ft))

        main_d = []
        associates = []

        for ind, d in enumerate(meta_jsons):
            p = meta_files[ind][:meta_files[ind].find('metadata')]
            print(f"Scanning path: {p}")
            main_data = {
                'url': d['URL'],
                'index_title': d['Index Title'],
                'origin_title': d['Origin Title'],
                'gallery_id': int(d['Gallery ID'].replace("#", '')),
                'pages': int(d['Pages']),
                'uploaded': d.get('Uploaded', ''),
                'path': p,
                'device_tag': tag,
                'meta_version': 'djsV2'
            }

            if main_data['uploaded'] is None:
                main_data['uploaded'] = ''

            files = [f for f in os.listdir(main_data['path']) if 'metadata' not in f and 'Thumbs' not in f]
            sort_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
            with open(f"{p}{os.sep}{sort_files[0]}", 'rb') as f1:
                main_data['preview'] = f1.read()
            with open(f"{p}{os.sep}{list_median(sort_files)}", 'rb') as f2:
                main_data['secondary_preview'] = f2.read()

            main_d.append(main_data)

            # 其他可选数据
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
            for a in characters:
                characters_data = {
                    'gallery_id': int(d['Gallery ID'].replace("#", '')),
                    'property': 'Characters',
                    'p_value': a.split("-count:")[0].strip()
                }
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

# if __name__ == '__main__':
#     scan_path = r"F:\manga"
#     url = r'sqlite:///C:\Users\ckhoi\PycharmProjects\MetaCollectorFramework\djs.db'
