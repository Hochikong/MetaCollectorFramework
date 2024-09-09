# -*- coding: utf-8 -*-
# @Time    : 2024/9/10 3:42
# @Author  : Hochikong
# @FileName: Task.py

from typing import List
from pydantic import BaseModel


class SingleTask(BaseModel):
    url: str


class BulkTasks(BaseModel):
    urls: List[str]
