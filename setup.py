# -*- coding: utf-8 -*-
# @Time    : 2022/5/17 23:46
# @Author  : Hochikong
# @FileName: setup.py

from setuptools import setup, find_packages

setup(
    name='MCF',
    version='1.0.0',

    description='Meta Collector Framework',

    author='Hochikong',
    author_email='ckhoidea@hotmail.com',

    classifiers=['License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
                 'Programming Language :: Python :: 3.8',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    entry_points={
        'console_scripts': [
            'mcf_collect=MetaCollector.crawler_startup:cli_launch',

        ],

        # namespace -> taodata   name -> shopaddr
        'taodata': [
            'shopaddr = cpir_core.taodata.plugins.shopaddr_collector:ShopAddrCollector',
        ],

    },

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
)
