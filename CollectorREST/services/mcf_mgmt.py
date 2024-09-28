import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime as dt
from typing import Optional
from uuid import uuid4

import psutil
from cachetools import LRUCache
from loguru import logger

from MetaCollector.base.utils.ind_logger.report import beauty_dict_report
from MetaCollector.base.utils.selenium.factory import yaml_loader
from MetaCollector.crawler.agent import CollectAgent

logger.remove()


@dataclass
class Args(object):
    # json string
    cfg: str
    debug: str
    # json string
    notify: Optional[str] = None
    xdisplay: Optional[bool] = None
    forward: Optional[int] = None
    all_notify: Optional[bool] = None

    @classmethod
    def from_dict(cls, mapping: dict):
        args = cls(mapping['cfg'], mapping['debug'],
                   mapping.get('notify', None), mapping.get('xdisplay', False),
                   mapping.get('forward', None), mapping.get('all_notify', None))
        return args


@dataclass
class RuntimeStorageTask(object):
    task: str
    instance_id: str
    instance_tag: str
    status: str
    start_time: str
    end_time: Optional[str]


class AgentWrapper(object):
    def __init__(self, logger: any, args: Args):
        self._args = args
        self.logger = logger
        self.cfg_content = yaml_loader(args.cfg)
        self.notify_content = None
        # noVNC forward process
        self.proc = None
        self.xvfb_launch = False
        self.agent = CollectAgent()
        # connect to remote chrome？
        self.connect_to_remote_done = False

        agent = self.agent
        logger.info("加载配置文件中...")
        if args.notify:
            agent.load_cfg_from_files(args.cfg, args.notify, args.debug)
        else:
            agent.load_cfg_from_files(args.cfg, debug_mode=args.debug)
        logger.info("加载配置文件完毕")

        if args.all_notify:
            agent.enable_all_notify()

        if args.xdisplay:
            # 启动vnc转发服务的两种途径
            if agent.yaml_cfg['selenium'].get('forward_port', -1) != -1:
                if agent.yaml_cfg['selenium'].get('xdisplay_backend', '') == 'xvnc':
                    source_port = agent.yaml_cfg['selenium']['xdisplay_port']
                    self.proc = subprocess.Popen(
                        f"novnc --listen {int(agent.yaml_cfg['selenium'].get('forward_port'))} --vnc localhost:{source_port}",
                        shell=True)
                self.xvfb_launch = agent.enable_xvfb()

            elif args.forward:
                if agent.yaml_cfg['selenium'].get('xdisplay_backend', '') == 'xvnc':
                    source_port = agent.yaml_cfg['selenium']['xdisplay_port']
                    target_port = int(args.forward)
                    self.proc = subprocess.Popen(f"novnc --listen {target_port} --vnc localhost:{source_port}",
                                                 shell=True)
                self.xvfb_launch = agent.enable_xvfb()
            else:
                self.xvfb_launch = agent.enable_xvfb()

    def stop(self):
        xvfb_launch = self.xvfb_launch
        agent = self.agent
        proc = self.proc

        if xvfb_launch:
            agent.stop_xvfb()

            if proc is not None:
                pid = proc.pid
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.kill()
                proc.terminate()
        agent.dispose()

    def goto_robot_check(self):
        agent = self.agent
        agent.hosted_instance.brow.get("https://nowsecure.nl")

    def goto_url(self, url: str):
        agent = self.agent
        agent.hosted_instance.brow.get(url)

    def launch_remote_chrome(self, command: str, connect_now: bool = False):
        agent = self.agent
        logger = self.logger

        if command.split(';')[-1] == 'ls':
            return list(agent.browser_holder.cmd_procs.keys())
        elif command.split(';')[-1].startswith('kill'):
            try:
                port = int(command.split(';')[-1].split(' ')[-1])
                for cmd in list(agent.browser_holder.cmd_procs.keys()):
                    if str(port) in cmd:
                        agent.browser_holder.kill_browser(cmd)
            except ValueError:
                logger.error("Port error can't parse to int")
            except Exception:
                logger.error(traceback.format_exc())
        else:
            try:
                port = int(command.split(';')[-1].split(' ')[0])
                ud_path = command.split(';')[-1].split(' ')[-1]
                agent.browser_holder.get_browser(agent.chrome_path, port, ud_path)
            except ValueError:
                logger.error("Port error can't parse to int")
            except Exception:
                logger.error(traceback.format_exc())

        if connect_now:
            # 启动完浏览器后直接连接chromedriver
            logger.info("启动chromedriver")
            agent.launch_for_drivers()
            self.connect_to_remote_done = True

    def run_driver(self, command: str, cfg_input: dict = None) -> dict:
        agent = self.agent
        logger = self.logger

        if cfg_input is None:
            cfg_input = self.cfg_content

        if not self.connect_to_remote_done:
            logger.info("启动chromedriver")
            agent.launch_for_drivers()

        namespace_dr = command.split(";")[-1]
        ns = namespace_dr.split(":")[0]
        dr = namespace_dr.split(":")[1]

        run_results = {}

        agent.load_driver(ns, dr)
        logger.info(f"驱动{dr}已加载完毕")
        logger.info("运行驱动：{}".format(dr))
        r = agent.run_extension(dr, agent.hosted_instance, cfg_input, auto_exit=False,
                                range=False)
        run_results[dr] = (r, agent.plugin_run_desc)

        if agent.em:
            agent.em.update_subject("run已执行全部模块")
            agent.em.quick_send(f"取数任务完成, 统计报告如下：\n\n{beauty_dict_report(run_results)}")
        else:
            logger.info("run已执行全部模块")
            logger.info(f"取数任务完成, 统计报告如下：\n\n{beauty_dict_report(run_results)}")

        run_stats = agent.driver_mgr.driver.get_plugin_info()
        return run_stats


class RuntimeStorage(object):
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=16)
        self.agents_scope = {}
        self.current_tasks = LRUCache(maxsize=500)
        self.task_results = LRUCache(maxsize=500)


class AgentFactoryWrapper(object):
    def __init__(self):
        self.rs = RuntimeStorage()
        self.logger_child = None

    def _job_new_instance(self, task_id: str, instance_id: str, cfg: Args):
        rs = self.rs
        self.logger_child = deepcopy(logger)
        self.logger_child.add(f"MCF_LOGS/instance_{instance_id}.log", colorize=True,
                              format='[{time:YYYY-MM-DD} {time:HH:mm:ss}][{file}.{function}:{line}][{level}] -> {message}',
                              level="INFO")
        try:
            self.logger_child.info(cfg)
            agent = AgentWrapper(self.logger_child, cfg)
            print(instance_id)
            self.rs.agents_scope[instance_id] = agent
            print("create done")
            rs.current_tasks[task_id].status = 'Done'
            rs.current_tasks[task_id].end_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.logger_child.error(traceback.format_exc())

    def _job_stop_instance(self, task_id: str, instance_id: str):
        rs = self.rs

        agent: AgentWrapper = self.rs.agents_scope[instance_id]
        agent.stop()

        del rs.agents_scope[instance_id]

        rs.current_tasks[task_id].status = 'Done'
        rs.current_tasks[task_id].end_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    def _job_goto_url(self, task_id: str, instance_id: str, url: Optional[str]):
        rs = self.rs

        agent: AgentWrapper = self.rs.agents_scope[instance_id]
        if url is None:
            agent.goto_robot_check()
        else:
            agent.goto_url(url)

        rs.current_tasks[task_id].status = 'Done'
        rs.current_tasks[task_id].end_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    def _job_launch_remote_chrome(self, task_id: str, instance_id: str, cmd: str):
        rs = self.rs

        agent: AgentWrapper = self.rs.agents_scope[instance_id]
        agent.launch_remote_chrome(cmd)

        rs.current_tasks[task_id].status = 'Done'
        rs.current_tasks[task_id].end_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    def _job_run_driver(self, task_id: str, instance_id: str, cmd: str, cfg_input: dict):
        rs = self.rs

        agent: AgentWrapper = self.rs.agents_scope[instance_id]
        stats = agent.run_driver(cmd, cfg_input)

        rs.current_tasks[task_id].status = 'Done'
        rs.current_tasks[task_id].end_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')

        rs.task_results[task_id] = stats
        self.logger_child.info(f"已完成的任务: {stats}")

    def create_agent(self, agent_tag: str, cfg: Args, not_pool: bool = False):
        rs = self.rs

        if list(rs.agents_scope.keys()) == 0:
            rs.pool.shutdown(False)
            rs.pool = ThreadPoolExecutor(max_workers=8)

        task_id = str(uuid4())
        instance_id = str(uuid4())
        rs.current_tasks[task_id] = RuntimeStorageTask(task='create_mcf_instance',
                                                       instance_id=instance_id,
                                                       instance_tag=agent_tag,
                                                       status='Not Done',
                                                       start_time=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                       end_time=None)
        if not_pool:
            self._job_new_instance(task_id, instance_id, cfg)
        else:
            rs.pool.submit(self._job_new_instance, task_id, instance_id, cfg)

        return {'task_id': task_id, 'instance_id': instance_id}

    def stop_agent(self, agent_tag: str, instance_id: str, not_pool=False):
        rs = self.rs

        task_id = str(uuid4())
        rs.current_tasks[task_id] = RuntimeStorageTask(task='stop_mcf_instance',
                                                       instance_id=instance_id,
                                                       instance_tag=agent_tag,
                                                       status='Not Done',
                                                       start_time=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                       end_time=None)

        rs.pool.submit(self._job_stop_instance, task_id, instance_id)

        if not_pool:
            self._job_stop_instance(task_id, instance_id)
        else:
            rs.pool.submit(self._job_stop_instance, task_id, instance_id)

        return {'task_id': task_id}

    def goto_url(self, agent_tag: str, instance_id: str, url: str = None, not_pool: bool = False):
        rs = self.rs

        task_id = str(uuid4())
        rs.current_tasks[task_id] = RuntimeStorageTask(task='goto_mcf_instance',
                                                       instance_id=instance_id,
                                                       instance_tag=agent_tag,
                                                       status='Not Done',
                                                       start_time=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                       end_time=None)

        if not_pool:
            self._job_goto_url(task_id, instance_id, url)
        else:
            rs.pool.submit(self._job_goto_url, task_id, instance_id, url)
        return {'task_id': task_id}

    def launch_remote_chrome(self, agent_tag: str, instance_id: str, command: str, not_pool: bool = False):
        rs = self.rs

        task_id = str(uuid4())
        rs.current_tasks[task_id] = RuntimeStorageTask(task='launch_remote_chrome',
                                                       instance_id=instance_id,
                                                       instance_tag=agent_tag,
                                                       status='Not Done',
                                                       start_time=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                       end_time=None)

        if not_pool:
            self._job_launch_remote_chrome(task_id, instance_id, command)
        else:
            rs.pool.submit(self._job_launch_remote_chrome, task_id, instance_id, command)
        return {'task_id': task_id}

    def run_driver(self, agent_tag: str, instance_id: str, cmd: str, cfg_input: str, not_pool: bool = False):
        rs = self.rs

        task_id = str(uuid4())
        rs.current_tasks[task_id] = RuntimeStorageTask(task='run_driver',
                                                       instance_id=instance_id,
                                                       instance_tag=agent_tag,
                                                       status='Not Done',
                                                       start_time=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                       end_time=None)

        cfg_input = yaml_loader(cfg_input)

        if not_pool:
            self._job_run_driver(task_id, instance_id, cmd, cfg_input)
        else:
            rs.pool.submit(self._job_run_driver, task_id, instance_id, cmd, cfg_input)
        return {'task_id': task_id}
