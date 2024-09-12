# -*- coding: utf-8 -*-
# @Time    : 2024/9/10 3:41
# @Author  : Hochikong
# @FileName: tasks.py

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from CollectorREST.domains.tasks import SingleTaskReceive, BulkTasksReceive, TaskRowCreate
from CollectorREST.repository import basic_crud_repository
from CollectorREST.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/tasks/single/", tags=['tasks'])
def receive_task(task: SingleTaskReceive, db: Session = Depends(get_db)):
    created_task = TaskRowCreate(task_uid=str(uuid.uuid4()), task_content=task.url, task_status=3,
                                 driver_info='test_driver')
    status = basic_crud_repository.create_task(db, created_task)
    return {'status': status}


@router.get('/tasks/{uid}', tags=['tasks'])
def get_single_task(uid: str, db: Session = Depends(get_db)):
    return basic_crud_repository.get_task_by_uid(db, uid)


@router.post("/tasks/bulk/", tags=['tasks'])
def receive_tasks(tasks: BulkTasksReceive):
    return tasks
