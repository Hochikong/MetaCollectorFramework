# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 18:02
# @Author  : Hochikong
# @FileName: main_mcf_holder.py
import concurrent.futures
import asyncio
import time
import logging
from ..services.mcf_mgmt import Args
from ..services.mcf_mgmt import AgentFactoryWrapper
from ..services.task_queue_maintainer import TaskQueueMaintainer

from ..app_config import MCF_CONFIG, MAIN_MCF_REMOTE_CHROME_COMMAND

logger = logging.getLogger('main_app')


class MainMCF(object):
    def __init__(self, agent_service: AgentFactoryWrapper, queue_maintainer: TaskQueueMaintainer, logger: any):
        self.logger = logger
        self.agent_service = agent_service
        self.queue_maintainer = queue_maintainer
        self.execute_driver_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.stop_flag = False

        agent_service = self.agent_service
        task = agent_service.create_agent('main', Args(MCF_CONFIG, 'yes'), not_pool=True)
        task_id = task['task_id']
        logger.info(agent_service.rs.current_tasks[task_id].status)
        instance_id = agent_service.rs.current_tasks[task_id].instance_id
        logger.info(f"Self instance id is {instance_id}, task id is {task_id}")

        agent_service.launch_remote_chrome('main', instance_id, MAIN_MCF_REMOTE_CHROME_COMMAND, True)
        logger.info(f"Self instance remote chrome is on")

    def queue_consumer(self, instance_id: str):
        logger = self.logger
        queue_m = self.queue_maintainer
        agent_service = self.agent_service

        while True:
            if self.stop_flag:
                logger.info("Stop consumer periodic task")
                break
            else:
                task = queue_m.get_task_from_queue()
                if task['driver_info'] != 'EMPTY' and len(task['tasks']) > 0:
                    cfg_path = task['cfg_path']
                    agent_service.run_driver('main', instance_id, )
