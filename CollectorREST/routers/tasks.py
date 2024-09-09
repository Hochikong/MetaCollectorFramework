# -*- coding: utf-8 -*-
# @Time    : 2024/9/10 3:41
# @Author  : Hochikong
# @FileName: tasks.py

from fastapi import APIRouter
from CollectorREST.entities.tasks import SingleTask, BulkTasks

router = APIRouter()


@router.post("/tasks/single/", tags=['tasks'])
def receive_task(task: SingleTask):
    return task


@router.post("/tasks/bulk/", tags=['tasks'])
def receive_tasks(tasks: BulkTasks):
    return tasks
