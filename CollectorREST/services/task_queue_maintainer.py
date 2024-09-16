from queue import Queue
from fastapi import Depends
from sqlalchemy.orm import Session
from ..repository.basic_crud_repository import get_tasks_by_status, update_task_status

from ..database import SessionLocal


class TaskQueueMaintainer:
    def __init__(self, logger: any):
        self.logger = logger
        self.queue = Queue(maxsize=0)

    def load_pending_tasks_from_db(self):
        logger = self.logger
        queue = self.queue

        db_session: Session = SessionLocal()
        tasks = get_tasks_by_status(db_session, status=3)

        driver_infos = set([i.driver_info for i in tasks])
        tasks_group_by_driver = []
        for driver_info in driver_infos:
            tmp = {'driver_info': driver_info, 'tasks': [i for i in tasks if i.driver_info == driver_info]}
            tasks_group_by_driver.append(tmp)

        logger.info(f"Current size before -> {self.queue.qsize()}")
        logger.info("Putting not done tasks into queue")
        for task in tasks_group_by_driver:
            queue.put(task)
        logger.info(f"Current size after -> {self.queue.qsize()}")

        db_session.close()

    def update_task_status_by_uuid(self, uid: str, status: int):
        logger = self.logger
        db_session: Session = SessionLocal()
        update_task_status(db_session, uid, status)
        logger.info(f"Updated status of task {uid} to {status}")
        db_session.close()

    def get_task_from_queue(self):
        logger = self.logger
        queue = self.queue

        if self.queue.empty():
            logger.info("Queue is empty")
            return {'driver_info': 'EMPTY', 'tasks': []}
        else:
            return queue.get(timeout=5)
