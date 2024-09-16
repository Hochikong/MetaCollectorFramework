import datetime

from sqlalchemy.orm import Session
from typing import List
from ..entities import db_entity
from ..domains import tasks


def get_task_by_uid(db: Session, uuid: str) -> db_entity.TaskListEntity:
    return db.query(db_entity.TaskListEntity).filter(db_entity.TaskListEntity.task_uid == uuid).one()


def get_tasks_by_status(db: Session, status: int) -> List[db_entity.TaskListEntity]:
    return db.query(db_entity.TaskListEntity).filter(db_entity.TaskListEntity.task_status == status).all()


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[db_entity.TaskListEntity]:
    return db.query(db_entity.TaskListEntity).offset(skip).limit(limit).all()


def create_task(db: Session, task_params: tasks.TaskRowCreate) -> bool:
    new_task = db_entity.TaskListEntity(**task_params.model_dump(), deleted_at=datetime.datetime(2077, 1, 1, 8, 0, 0,0))
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return True


def update_task_status(db: Session, uuid: str, status: int) -> bool:
    task = get_task_by_uid(db, uuid)
    task.task_status = status
    db.commit()
    db.refresh(task)
    return True
