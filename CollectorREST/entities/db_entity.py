import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime

from ..database import Base

# db entity可以用于数据库操作，或者用于view函数的返回，但不能作为view函数的输入

class BaseMixin:
    """model的基类,所有model都必须继承"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                        index=True)
    deleted_at = Column(DateTime)


class TaskListEntity(Base, BaseMixin):
    __tablename__ = "tasks_list"

    task_uid = Column(String(100), unique=True, index=True)
    # 任务的主要内容，即URL
    task_content = Column(String(200))
    # 任务状态，主要是
    # , commment = '任务状态：PENDING -> 3 / ONGOING -> 0 / DONE -> 1 / ERROR -> 2'
    task_status = Column(Integer)
    # 本任务使用什么驱动程序执行
    driver_info = Column(String(50))
    # 附加的配置文件key
    attach_cfg_key = Column(String(100))
