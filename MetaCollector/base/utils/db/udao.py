import time
import traceback
from typing import List
import concurrent.futures as futures
from concurrent.futures import thread

from sqlalchemy import Table, MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class UniversalDAO(object):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.md = None
        self.engine = None
        self.session: Session = None
        self.table_object: Table = None
        self.auto_dispose: bool = True
        self.__table_caches = {}

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
        if self.auto_dispose:
            self.dispose()

    def connect(self):
        self._connect()

    def disconnect(self):
        self.auto_dispose = True
        self._disconnect()

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
        self._connect()
        self.table_object = Table(table, self.md, autoload=True, autoload_with=self.engine)
        succeed = 0
        try:
            self.session.execute(self.table_object.insert(), data)
            self.session.commit()
            succeed = 1
        except Exception as e:
            em = f"{e}\n{traceback.format_exc()}"
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

    def __new_table(self, name):
        return Table(name, self.md, autoload=True, autoload_with=self.engine)

    def __get_table_object(self, table_name: str):
        if table_name not in self.__table_caches.keys():
            # self.logger.info("建立新的表对象并缓存")
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.__new_table, table_name)
                try:
                    table_object = future.result(15)
                except futures.TimeoutError:
                    # print('建表对象超时')
                    self.engine.dispose()
                    del self.engine
                    del self.md
                    time.sleep(2)
                    self.md = MetaData()
                    self.engine = create_engine(self.db_url, connect_args={'connect_timeout': 120}, pool_pre_ping=True,
                                                pool_recycle=3600)
                    table_object = self.__new_table(table_name)
                executor._threads.clear()
                futures.thread._threads_queues.clear()
                executor.shutdown(wait=False)

            self.__table_caches[table_name] = table_object
            return table_object
        else:
            # self.logger.info("从已有的表对象列表获取实例")
            return self.__table_caches[table_name]

    def get_table_object(self, table_name):
        return self.__get_table_object(table_name)
