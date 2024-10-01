# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 18:02
# @Author  : Hochikong
# @FileName: main_mcf_holder.py
import concurrent.futures
import asyncio
import os
import time
import logging
import traceback
from queue import Queue
from MetaCollector.base.utils.selenium.factory import yaml_loader, yaml_writer
from ..services.mcf_mgmt import AgentFactoryWrapper, Args, AgentWrapper
from ..services.task_queue_maintainer import TaskQueueMaintainer

from ..app_config import MCF_CONFIG, MAIN_MCF_REMOTE_CHROME_COMMAND


class MainMCF(object):
    def __init__(self, agent_service: AgentFactoryWrapper, queue_maintainer: TaskQueueMaintainer, logger: any):
        self.logger = logger
        self.agent_service = agent_service
        self.queue_maintainer = queue_maintainer
        self.common_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.task_id_queue = Queue(maxsize=0)
        self.stop_flag = False
        self.mcf_lock = False

        agent_service = self.agent_service
        task = agent_service.create_agent('main', Args(MCF_CONFIG, 'yes'), not_pool=True)
        task_id = task['task_id']
        logger.info(agent_service.rs.current_tasks[task_id].status)
        instance_id = agent_service.rs.current_tasks[task_id].instance_id
        logger.info(f"Self instance id is {instance_id}, task id is {task_id}")

        agent_service.launch_remote_chrome('main', instance_id, MAIN_MCF_REMOTE_CHROME_COMMAND, True)
        logger.info(f"Self instance remote chrome is on")

        self.future = self.common_pool.submit(self.queue_consumer, instance_id)
        self.future1 = self.common_pool.submit(self.task_updater)

    @staticmethod
    def generate_runtime_main_cfg(source_main_cfg_path: str, attach_cfg_key: str, attach_cfg_path: str) -> str:
        """
        Write new config to MCF_CONFIG file to replace its attach_cfg contents

        :param source_main_cfg_path
        :param attach_cfg_key
        :param attach_cfg_path
        :return:
        """
        if attach_cfg_key == 'NONE':
            return source_main_cfg_path
        else:
            content = yaml_loader(source_main_cfg_path)
            if 'attach_cfg' in content.keys():
                content['attach_cfg'][attach_cfg_key] = attach_cfg_path
            else:
                content['attach_cfg'] = {}
                content['attach_cfg'][attach_cfg_key] = attach_cfg_path

            yaml_writer(source_main_cfg_path, content)
            return source_main_cfg_path

    def queue_consumer(self, instance_id: str):
        logger = self.logger
        queue_m = self.queue_maintainer
        agent_service = self.agent_service

        # wait for chrome ready
        time.sleep(180)

        while True:
            if self.mcf_lock is True:
                logger.info("MainMCF currently is locked")
                time.sleep(60)
                continue
            else:
                logger.info("MainMCF currently is unlocked")

            if self.stop_flag:
                logger.info("Stop queue consumer periodic task")
                break
            else:
                try:
                    task = queue_m.get_task_from_queue()
                    driver_info_and_cmd_param = task['driver_info']
                    if driver_info_and_cmd_param != 'EMPTY' and len(task['tasks']) > 0:

                        # set all task ongoing
                        task_rows = task['tasks']
                        for tr in task_rows:
                            self.queue_maintainer.update_task_status_by_uuid(tr.task_uid, 0)

                        attach_cfg_key = task['attach_cfg_key']
                        attach_cfg = task['cfg_path']
                        logger.info(f"Running driver: {driver_info_and_cmd_param}")

                        new_main_cfg_path = self.generate_runtime_main_cfg(MCF_CONFIG, attach_cfg_key, attach_cfg)

                        task_id = agent_service.run_driver('main', instance_id, f'/run;{driver_info_and_cmd_param}',
                                                           new_main_cfg_path)['task_id']
                        logger.info(f"Task ID: {task_id}")
                        logger.info("Task submit done")
                        self.task_id_queue.put({'task_rows': task_rows, 'task_id': task_id})
                        time.sleep(60)
                    else:
                        time.sleep(30)
                        continue
                except Exception:
                    logger.error(traceback.format_exc())

    def task_updater(self):
        logger = self.logger
        queue_m = self.queue_maintainer
        agent_service = self.agent_service

        while True:
            if self.stop_flag:
                logger.info("Stop task_updater periodic task")
                break
            else:
                if self.task_id_queue.empty():
                    time.sleep(30)
                else:
                    task_cred = self.task_id_queue.get(timeout=10)
                    logger.info(f"task cred: {task_cred}")
                    try:
                        task_id = task_cred['task_id']
                        done = False
                        while not done:
                            try:
                                run_stat: dict = agent_service.rs.task_results[task_id]
                                logger.info(run_stat)
                                # set all tasks done or error
                                task_rows = task_cred['task_rows']

                                for tr in task_rows:
                                    logger.warning(tr.task_content)
                                    if tr.task_content in run_stat['done_tasks']:
                                        queue_m.update_task_status_by_uuid(tr.task_uid, 1)
                                    else:
                                        queue_m.update_task_status_by_uuid(tr.task_uid, 2)

                                done = True
                            except KeyError:
                                # logger.warning(traceback.format_exc())
                                time.sleep(30)
                                continue

                    except Exception:
                        logger.warning(traceback.format_exc())
                    time.sleep(30)

    def stop_pool(self):
        self.stop_flag = True
        self.common_pool.shutdown(wait=True)
