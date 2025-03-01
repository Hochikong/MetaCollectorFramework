# -*- coding: utf-8 -*-
# @Time    : 2024/9/10 3:41
# @Author  : Hochikong
# @FileName: tasks_controller.py

import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from djsplugins.MCF.collector_rest_utils.middleware import CollectorRESTMiddleware
from ..domains.tasks import SingleTaskReceive, BulkTasksReceive, TaskRowCreate
from ..dependencies import get_queue_maintainer, get_main_mcf
from ..repository import basic_crud_repository
from ..database import SessionLocal
from ..services.task_queue_maintainer import TaskQueueMaintainer
from ..services.main_mcf_holder import MainMCF

router = APIRouter()

logger = logging.getLogger('main_app')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


drivers_router = CollectorRESTMiddleware()
drivers_router.prepare(None, {})


@router.post("/tasks/single/", tags=['tasks'])
def receive_task(task: SingleTaskReceive, db: Session = Depends(get_db)):
    total_status = False
    logger.info(f"Received task: {task.url}")
    driver_info = drivers_router.get_router_output(task.url)
    for info in driver_info:
        created_task = TaskRowCreate(task_uid=str(uuid.uuid4()), task_content=task.url, task_status=3,
                                     driver_info=info['driver'], attach_cfg_key=info['attach_cfg_key'])
        status = basic_crud_repository.create_task(db, created_task)
        total_status = status
    return {'status': total_status}


@router.post("/tasks/bulk/", tags=['tasks'])
def receive_tasks(tasks: BulkTasksReceive, db: Session = Depends(get_db)):
    total_status = False
    params = tasks.params
    for url in tasks.urls:
        driver_info = drivers_router.get_router_output(url)
        for info in driver_info:
            created_task = TaskRowCreate(task_uid=str(uuid.uuid4()), task_content=url, task_status=3,
                                         driver_info=info['driver'], attach_cfg_key=info['attach_cfg_key'],
                                         download_dir=params.get('download_child_dir', None))
            status = basic_crud_repository.create_task(db, created_task)
            total_status = status
    return {'status': total_status}


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


@router.get('/queue/stop_periodic_tasks', tags=['queue'])
def stop_periodic_task(queue_m: TaskQueueMaintainer = Depends(get_queue_maintainer),
                       main_mcf: MainMCF = Depends(get_main_mcf)):
    queue_m.stop_pool()
    main_mcf.stop_pool()
    return {'status': True}


@router.get('/queue/pop_one', tags=['queue'])
def get_task_from_queue(queue_m: TaskQueueMaintainer = Depends(get_queue_maintainer)):
    return queue_m.get_task_from_queue()
