# -*- coding: utf-8 -*-
# @Time    : 2024/9/10 3:41
# @Author  : Hochikong
# @FileName: tasks_controller.py

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from ..domains.tasks import SingleTaskReceive, BulkTasksReceive, TaskRowCreate
from ..dependencies import get_queue_maintainer, get_agent_service
from ..repository import basic_crud_repository
from ..database import SessionLocal
from ..services.task_queue_maintainer import TaskQueueMaintainer

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


@router.post("/tasks/bulk/", tags=['tasks'])
def receive_tasks(tasks: BulkTasksReceive):
    return tasks


@router.get('/tasks/{uid}', tags=['tasks'])
def get_single_task(uid: str, db: Session = Depends(get_db)):
    try:
        return basic_crud_repository.get_task_by_uid(db, uid)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get('/tasks/status/', tags=['tasks'])
def get_tasks_by_status(code: int, db: Session = Depends(get_db)):
    return basic_crud_repository.get_tasks_by_status(db, code)


@router.get('/queue/size', tags=['queue'])
def get_current_queue_size(queue_m: TaskQueueMaintainer = Depends(get_queue_maintainer)):
    return {'size': queue_m.queue.qsize()}


# @router.get('/queue/fetch_one', tags=['queue'])
# def get_task_from_queue(queue_m: TaskQueueMaintainer = Depends(get_queue_maintainer)):
#     return queue_m.get_task_from_queue()

