import concurrent
import datetime
import os
import time
import hashlib
from copy import deepcopy
from queue import Queue
from sqlalchemy.orm import Session
from MetaCollector.base.utils.selenium.factory import yaml_loader, yaml_writer
from ..database import SessionLocal
from ..repository.basic_crud_repository import get_tasks_by_status, update_task_status
from ..app_config import TASK_TEMPLATE_CONFIG as template_config_path
from ..app_config import TEMPORARY_CONFIG_DIR


class TaskQueueMaintainer:
    def __init__(self, logger: any):
        self.logger = logger
        self.queue = Queue(maxsize=0)
        self.stop_flag = False
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.future = self.pool.submit(self._load_pending_tasks_periodically)
        self.template = yaml_loader(template_config_path)

    def _load_pending_tasks_periodically(self):
        logger = self.logger
        while True:
            if self.stop_flag:
                logger.info("Stop periodic tasks")
                break
            elif self.stop_flag is False and self.queue.empty():
                logger.info("Start to load tasks from db")
                self.load_pending_tasks_from_db()
                time.sleep(60)
            else:
                # 10mins
                logger.info("Skip to load tasks from db")
                time.sleep(20)

    def load_pending_tasks_from_db(self):
        logger = self.logger
        queue = self.queue

        db_session: Session = SessionLocal()
        tasks = get_tasks_by_status(db_session, status=3)

        driver_infos = set([i.driver_info for i in tasks])
        tasks_group_by_driver = []
        for driver_info in driver_infos:
            tasks = [i for i in tasks if i.driver_info == driver_info]

            author = f"{driver_info}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            template = deepcopy(self.template)
            template['author'] = author
            template['targets'] = [t.task_content for t in tasks]
            hashcode_text = ','.join(template['targets'])
            hashcode = hashlib.md5(hashcode_text.encode('utf-8')).hexdigest()
            cfg_path = f"{TEMPORARY_CONFIG_DIR}{os.sep}{hashcode}.yaml"
            yaml_writer(cfg_path, template)

            tmp = {'driver_info': driver_info, 'tasks': tasks, 'cfg_path': cfg_path}
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

    def stop_pool(self):
        self.stop_flag = True
        self.pool.shutdown(wait=True)
