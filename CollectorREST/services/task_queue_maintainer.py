from queue import Queue
from fastapi import Depends
from sqlalchemy.orm import Session
from ..repository.basic_crud_repository import get_tasks_by_status

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

        logger.info(f"Current size before -> {self.queue.qsize()}")
        logger.info("Putting not done tasks into queue")
        for task in tasks:
            queue.put(task)
        logger.info(f"Current size after -> {self.queue.qsize()}")

        db_session.close()
