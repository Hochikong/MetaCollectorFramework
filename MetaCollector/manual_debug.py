# -*- coding: utf-8 -*-
# @Time    : 2022/5/22 0:31
# @Author  : Hochikong
# @FileName: manual_debug.py

from MetaCollector.crawler_startup import *

ca = CollectAgent()
ca.load_cfg_from_files(r'C:\Users\ckhoi\PycharmProjects\MetaCollectorFramework\mcf_cfg.yml', debug_mode='yes')
ca.launch_for_drivers()
coll = ca.hosted_instance
driver = coll.brow
