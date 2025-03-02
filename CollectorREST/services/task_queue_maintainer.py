import datetime
import os
import time
import hashlib
import concurrent.futures
import traceback
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
            try:
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
            except Exception:
                logger.warning(traceback.format_exc())
                time.sleep(30)

    def load_pending_tasks_from_db(self):
        logger = self.logger
        queue = self.queue

        db_session: Session = SessionLocal()
        tasks = get_tasks_by_status(db_session, status=3)

        driver_infos = set([i.driver_info for i in tasks])
        tasks_group_by_driver = []
        for driver_info in driver_infos:
            tasks = [i for i in tasks if i.driver_info == driver_info]

            # 不指定子下载目录的任务
            no_child_dirs_tasks = [t for t in tasks if t.download_dir is None]
            if len(no_child_dirs_tasks) > 0:
                author = f"{driver_info}_{datetime.datetime.now().strftime('%Y%m%d_%H')}"
                author = author.replace(":", "-")
                template = deepcopy(self.template)
                template['author'] = author
                template['targets'] = [t.task_content for t in no_child_dirs_tasks]

                same_attach_cfg_key = tasks[0].attach_cfg_key
                hashcode_text = ','.join(template['targets'])
                hashcode = hashlib.md5(hashcode_text.encode('utf-8')).hexdigest()
                cfg_path = f"{TEMPORARY_CONFIG_DIR}{os.sep}{hashcode}.yaml"
                yaml_writer(cfg_path, template)

                tmp = {'driver_info': driver_info, 'tasks': no_child_dirs_tasks, 'cfg_path': cfg_path,
                       'attach_cfg_key': same_attach_cfg_key}
                tasks_group_by_driver.append(tmp)

            # 指定了子下载任务的目录
            distinct_child_dirs = list(set([t.download_dir for t in tasks if isinstance(t.download_dir, str)]))
            if len(distinct_child_dirs) > 0:
                for download_child_dir in distinct_child_dirs:
                    sub_tasks = [t for t in tasks if t.download_dir == download_child_dir]
                    author = f"{driver_info}_{datetime.datetime.now().strftime('%Y%m%d_%H')}"
                    author = author.replace(":", "-")
                    template = deepcopy(self.template)
                    template['author'] = author
                    template['targets'] = [t.task_content for t in sub_tasks]

                    if template['target_save_dir'].endswith(os.sep):
                        template['target_save_dir'] += (download_child_dir + os.sep)
                    else:
                        template['target_save_dir'] += (os.sep + download_child_dir + os.sep)

                    same_attach_cfg_key = sub_tasks[0].attach_cfg_key
                    hashcode_text = ','.join(template['targets'])
                    hashcode = hashlib.md5(hashcode_text.encode('utf-8')).hexdigest()
                    cfg_path = f"{TEMPORARY_CONFIG_DIR}{os.sep}{hashcode}.yaml"
                    yaml_writer(cfg_path, template)

                    tmp = {'driver_info': driver_info, 'tasks': sub_tasks, 'cfg_path': cfg_path,
                           'attach_cfg_key': same_attach_cfg_key}
                    tasks_group_by_driver.append(tmp)

        logger.info(f"Current size before -> {self.queue.qsize()}")
        logger.info("Putting not done tasks into queue")
        for task in tasks_group_by_driver:
            queue.put(task)
        logger.info(f"Current size after -> {self.queue.qsize()}")

        db_session.close()

    def update_task_status_by_uuid(self, task_uid: str, status: int):
        """
        status：PENDING -> 3 / ONGOING -> 0 / DONE -> 1 / ERROR -> 2

        :param task_uid:
        :param status:
        :return:
        """
        logger = self.logger
        db_session: Session = SessionLocal()
        update_task_status(db_session, task_uid, status)
        logger.info(f"Updated status of url task {task_uid} to {status}")
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
