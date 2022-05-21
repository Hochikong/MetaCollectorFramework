from sqlalchemy import Table, MetaData
from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.orm import Session


class DAO(object):
    def __init__(self, db_url: str):
        """初始化DAO对象

        :param db_url: sqlalchemy支持的url格式
        """
        self.md = MetaData()
        self.engine = create_engine(db_url)
        self.session = Session(self.engine)
        self.table_map = {}

    def load_table(self, table_name: str, key: str = None) -> bool:
        """尝试加载指定名称的表格

        :param table_name: 表的名字
        :param key: 用于指定查找该表时使用的键
        :return: 成功加载时返回True，否则为False
        """
        if key is None:
            key = table_name

        if key in self.table_map.keys():
            print('不可使用重复的键')
            return False

        try:
            tmp = Table(table_name, self.md, autoload=True, autoload_with=self.engine)
            self.table_map[key] = tmp
            return True
        except NoSuchTableError:
            return False

    def insert(self, key: str, data_list: list) -> int:
        """把符合格式的数据插入到数据库中，再一次性提交

        :param key: 用于指定查找该表时使用的键
        :param data_list: 一个列表A，列表里包含多个子列表A0, A1, A2...， 每个子列表都包含多个字典，每个字典代表表格的每一行数据
        :return: 返回插入行数
        """
        if key not in self.table_map.keys():
            print('目标表不存在')
            return 0

        for d_list in data_list:
            self.session.execute(self.table_map[key].insert(), d_list)

        try:
            self.session.commit()
            return len([item for sublist in data_list for item in sublist])
        except Exception as e:
            print(e)
            return 0

    def dispose(self):
        self.session.close()
