# -*- coding: utf-8 -*-
# @Time    : 2022/8/13 0:50
# @Author  : Hochikong
# @FileName: dao2.py

import traceback
from typing import List

from sqlalchemy import Table, MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session


class UniversalDAOV2(object):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.md = MetaData()
        self.engine = create_engine(self.db_url)
        self.__table_objects = {}

    def __get_table_object(self, table_name: str):
        if table_name not in self.__table_objects.keys():
            # self.logger.info("建立新的表对象并缓存")
            table_object = Table(table_name, self.md, autoload=True, autoload_with=self.engine)
            self.__table_objects[table_name] = table_object
            return table_object
        else:
            # self.logger.info("从已有的表对象列表获取实例")
            return self.__table_objects[table_name]

    def dispose(self):
        self.engine.dispose()

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
        session = scoped_session(sessionmaker(bind=self.engine))
        ses = Session()
        table_object = self.__get_table_object(table)
        succeed = 0
        try:
            ses.execute(table_object.insert(), data)
            ses.commit()
            succeed = 1
        except Exception as e:
            em = f"{e}\n{traceback.format_exc()}"
            ses.rollback()
            succeed = 0
        finally:
            session.remove()
            if succeed == 1:
                return True
            else:
                raise RuntimeError("导入报错: \n{}".format(em))

    def __import(self, data, table_name):
        session = scoped_session(sessionmaker(bind=self.engine))
        ses = Session()
        table_object = self.__get_table_object(table_name)
        succeed = 0
        try:
            ses.execute(table_object.insert(), data)
            ses.commit()
            succeed = 1
        except Exception as e:
            print("报错：{}".format(e))
            ses.rollback()
            succeed = 0
        finally:
            session.remove()
            return succeed == 1
