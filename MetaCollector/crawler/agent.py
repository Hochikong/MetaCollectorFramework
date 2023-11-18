# -*- coding: utf-8 -*-
# @Time    : 2022/5/21 20:04
# @Author  : Hochikong
# @FileName: agent.py
import datetime
import os
import subprocess
import time
import traceback
from time import sleep

import psutil
from stevedore import driver

from MetaCollector.base.utils.ind_logger.notify import EmailNotifierWrapper
from MetaCollector.base.utils.selenium.factory import DriverManagerMock, ChromeFactoryRemote
from MetaCollector.base.utils.selenium.factory import yaml_loader, chrome_factory, chrome_factory_uc, \
    chrome_factory_wireV2
from MetaCollector.crawler.Main import MCFDataCollector


class CollectAgent(object):
    def __init__(self):
        self.cfg_path = None
        self.yaml_cfg = None

        # selenium
        self.debug_or_not = None
        self.driver_path = None
        self.addition_args = None
        self.prefs = None

        # email
        self.email_file_path = None
        self.email_cfg = None
        # notify
        self.em: EmailNotifierWrapper = None

        # log部分的配置
        self.log_cfg = None
        self.sc_loc = None

        # runtime
        self.hosted_instance: MCFDataCollector = None
        self.driver_mgr = None
        self.enable_wire = False

        # xvfb
        self.v_display = None

        # 仅在取数报错时通知
        self.disable_unnecessary_notify = True

        self.chrome_version = 90

        self.xvfb_backend = 'xvfb'
        self.xvfb_port = 5904

        # 插件信息
        self.plugin_run_desc = ''

        # 是否启用novnc转发
        self.enable_noVNC = True
        self.noVNC_proc = None
        # 0 -> xvfb, 1 -> xvnc, 2 -> xvfb by xvfbwrapper
        self.x_channel = -1

        # 远程调试
        self.enable_remote = False
        self.remote_debug_port = 9222
        self.browser_holder = ChromeFactoryRemote()
        self.ud_path = None
        self.chrome_path = None

    def enable_all_notify(self):
        self.disable_unnecessary_notify = False

    def dispose(self):
        """
        集中释放资源

        :return:
        """
        try:
            self.stop_xvfb()

            if self.noVNC_proc is not None:
                pid = self.noVNC_proc.pid
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.kill()
                self.noVNC_proc.terminate()
                self.noVNC_proc = None

            if self.browser_holder is not None:
                self.browser_holder.kill_all()

        except Exception:
            print("关闭Agent时报错：{}".format(traceback.format_exc()))
            pass

    def stop_xvfb(self):
        if self.v_display:
            self.v_display.stop()

    def enable_xvfb(self) -> bool:
        if os.name == 'posix':

            # 2022-04-27 转由默认PyVirtualDisplay实现
            try:
                from pyvirtualdisplay import Display
                if self.xvfb_backend == 'xvfb':
                    self.v_display = Display(backend="xvfb", size=(1920, 1080))
                    self.v_display.start()
                    self.x_channel = 0
                elif self.xvfb_backend == 'xvnc':
                    if self.enable_noVNC:
                        if self.yaml_cfg['selenium'].get('forward_port', -1) != -1:
                            print("启用自带的novnc转发")
                            source_port = self.yaml_cfg['selenium']['xdisplay_port']
                            self.noVNC_proc = subprocess.Popen(
                                (f"novnc --listen {int(self.yaml_cfg['selenium'].get('forward_port'))} "
                                 f"--vnc localhost:{source_port}"),
                                shell=True)

                    # kill掉有相同rfbport的xvnc进程
                    vnc_processes = []
                    for proc in psutil.process_iter():
                        if f'-rfbport {self.xvfb_port}' in ' '.join(proc.cmdline()):
                            vnc_processes.append(proc)
                    for i in vnc_processes:
                        i.kill()
                        print(f"清除抢占xvnc端口: {self.xvfb_port} 的进程")
                    sleep(1)

                    self.v_display = Display(backend="xvnc", size=(1920, 1080), rfbport=self.xvfb_port,
                                             )
                    self.v_display.start()
                    self.x_channel = 1
                else:
                    self.v_display = Display(backend="xvfb", size=(1920, 1080))
                    self.v_display.start()
                    self.x_channel = 0.1
            except ModuleNotFoundError:
                from xvfbwrapper import Xvfb
                self.v_display = Xvfb()
                self.v_display.start()
                self.x_channel = 2

            return True
        else:
            return False

    def __cfg_interceptor(self, cfg_type: str = None):
        if cfg_type == 'file':
            self.yaml_cfg: dict = yaml_loader(self.cfg_path, encoding='utf-8')
            if self.email_file_path:
                self.email_cfg = yaml_loader(self.email_file_path, 'utf-8')['email']

        self.driver_path = self.yaml_cfg['selenium']['driver_path']
        self.addition_args = self.yaml_cfg['selenium']['addition_arguments']
        self.prefs = self.yaml_cfg['selenium']['prefs']
        self.log_cfg = self.yaml_cfg['log']
        self.sc_loc = self.log_cfg['screenshots']

        self.disable_insert = self.yaml_cfg['selenium'].get('disable_insert', False)
        self.enable_wire = self.yaml_cfg['selenium'].get('enable_wire', False)
        self.enable_uc = self.yaml_cfg['selenium'].get('enable_uc', False)

        self.enable_remote = self.yaml_cfg['selenium'].get('enable_remote', False)
        self.remote_debug_port = self.yaml_cfg['selenium'].get('remote_debug_port', 9222)
        self.chrome_path = self.yaml_cfg['selenium'].get('chrome_path', None)
        self.chrome_version = self.yaml_cfg['selenium'].get('version', 90)

        self.xvfb_backend = self.yaml_cfg['selenium'].get('xdisplay_backend', 'xvfb')
        self.xvfb_port = self.yaml_cfg['selenium'].get('xdisplay_port', 'xvfb')

    def load_cfg_from_files(self, cfg: str, notify: str = None, debug_mode: str = 'no'):
        self.cfg_path = cfg
        if notify:
            self.email_file_path = notify
        self.debug_or_not = debug_mode
        self.__cfg_interceptor('file')

    def load_cfg_from_dict(self, cfg_dict: dict, notify_dict: dict = None, debug_mode: str = 'no'):
        self.debug_or_not = debug_mode
        self.yaml_cfg: dict = cfg_dict
        if notify_dict:
            self.email_cfg = notify_dict['email']
        self.__cfg_interceptor()

    def get_instance(self):
        if self.debug_or_not == 'yes':
            headless = False
        else:
            headless = True

        # 检查相关目录是否存在，否则自动创建
        if self.addition_args:
            for c in self.addition_args:
                if c.startswith('--user-data-dir'):
                    try:
                        self.ud_path = c.split('=')[-1]
                        os.makedirs(self.ud_path)
                        print("已自动创建userdata dir")
                        break
                    except FileExistsError:
                        pass

        if self.prefs.get('download.default_directory', False):
            try:
                os.makedirs(self.prefs.get('download.default_directory'))
                print("已自动创建下载目录")
            except FileExistsError:
                pass

        if self.enable_wire:
            print("启用wire模式")
            self.hosted_instance = MCFDataCollector.build(
                chrome_factory_wireV2(self.driver_path, self.addition_args, self.prefs, headless),
                self.yaml_cfg, disable_insert=True, enable_wire=True, enable_uc=False
            )
            self.hosted_instance.log_info("以wire模式启动")
        elif self.enable_uc:
            print("启用uc模式")
            self.hosted_instance = MCFDataCollector.build(
                chrome_factory_uc(self.driver_path, self.addition_args, self.prefs, version=self.chrome_version,
                                  headless=headless),
                self.yaml_cfg, disable_insert=True, enable_wire=False, enable_uc=True
            )
            self.hosted_instance.log_info("以uc模式启动")
        elif self.enable_remote:
            print("启用remote模式")
            if self.chrome_path is None:
                raise AssertionError("没有提供chrome的可执行文件路径！")
            if self.ud_path is None:
                raise AssertionError("没有提供chrome的user_data_dir路径！")
            # self.browser_holder.get_browser(self.chrome_path, self.remote_debug_port, self.ud_path)
            time.sleep(2)
            self.hosted_instance = MCFDataCollector.build(
                self.browser_holder.chrome_factory_remote('127.0.0.1', self.remote_debug_port,
                                                          self.addition_args, self.prefs),
                self.yaml_cfg, disable_insert=True, enable_wire=False, enable_uc=True
            )
            self.hosted_instance.log_info("以remote模式启动")
        else:
            print("启用普通模式")
            self.hosted_instance = MCFDataCollector.build(
                chrome_factory(self.driver_path, self.addition_args, self.prefs, headless),
                self.yaml_cfg, disable_insert=self.disable_insert, enable_wire=False,
                enable_uc=False)
            self.hosted_instance.log_info("以普通模式启动")

    def launch_for_drivers(self):
        self.get_instance()

    def load_driver(self, namespace: str, name: str) -> bool:
        self.driver_mgr = driver.DriverManager(
            namespace=namespace,
            name=name,
            invoke_on_load=True
        )
        return True

    def load_driver_runtime(self, di) -> bool:
        self.driver_mgr = DriverManagerMock(di)
        return True

    def login_only(self) -> bool:
        try:
            self.hosted_instance.log_info("执行登陆操作\n")
            self.hosted_instance.login()
            sleep(3)
            return True
        except Exception as e:
            print(e, traceback.format_exc())
            path = '{}{}error_{}.png'.format(self.sc_loc, os.sep, int(datetime.datetime.now().timestamp()))
            self.hosted_instance.brow.save_screenshot(path)
            self.hosted_instance.log_info("截图已保存到{}".format(path))
            return False

    def logout_only(self) -> bool:
        try:
            self.hosted_instance.log_info("执行登出操作\n")
            self.hosted_instance.logout()
            sleep(3)
            return True
        except Exception as e:
            print(e, traceback.format_exc())
            return False

    def set_continue_mode_for_driver(self, on: bool) -> bool:
        return self.driver_mgr.driver.continue_mode(on)

    def get_worker_noted(self) -> str:
        return self.hosted_instance.worker_noted

    def run_extension(self, name: str, instance: MCFDataCollector, cfg_input: any,
                      auto_exit: bool = True, **kwargs) -> bool:
        """
        运行插件

        :param name: 插件名
        :param instance: MCFDataCollector的实例
        :param cfg_input: 配置文件的具体内容
        :param auto_exit: 在插件运行完/报错后是否自动退出，释放资源和关闭浏览器
        :param kwargs: 插件的附加参数
        :return:
        """
        notify_object = ''
        if self.driver_mgr is None:
            raise RuntimeError("尚未加载任何驱动，无法取数")
        else:

            if self.email_cfg:
                self.em = EmailNotifierWrapper(self.email_cfg['host'],
                                               self.email_cfg['username'],
                                               self.email_cfg['password'],
                                               self.email_cfg['from_'],
                                               "{}取数".format(self.driver_mgr.driver.get_name()),
                                               self.email_cfg['to'])
            else:
                notify_object = "{}取数".format(self.driver_mgr.driver.get_name())

            try:
                if isinstance(cfg_input, dict):
                    r0 = self.driver_mgr.driver.prepare(instance, cfg_input, **kwargs)
                else:
                    raise RuntimeError("输入内容不正确，无法prepare")

                # do
                if r0[0] is False:
                    raise RuntimeError(r0[-1])
                else:
                    instance.log_info(r0[-1])

                    if kwargs.get("range"):
                        if self.driver_mgr.driver.cfg.get('range', {}).get('monthly', False):
                            desc = "MCF-driver:{}-range_mode_months:{}->{}".format(name,
                                                                                   kwargs.get('range'),
                                                                                   [self.driver_mgr.driver.cfg[
                                                                                        'range']['months'][0],
                                                                                    self.driver_mgr.driver.cfg[
                                                                                        'range']['months'][-1]],
                                                                                   )
                        else:
                            desc = "MCF-driver:{}-range_mode:{}->{}".format(name,
                                                                            kwargs.get('range'),
                                                                            [self.driver_mgr.driver.cfg[
                                                                                 'range']['head'],
                                                                             self.driver_mgr.driver.cfg[
                                                                                 'range']['tail']],
                                                                            )
                    else:
                        # 日常取数模式，只取最新一日
                        desc = "MCF-driver:{}-range_mode:{}->{}".format(name,
                                                                        kwargs.get('range'),
                                                                        "latest date",
                                                                        )

                    self.plugin_run_desc = desc

                r1 = self.driver_mgr.driver.handle()
                if r1[0] is False:
                    raise RuntimeError(r1[-1])
                else:
                    instance.log_info(r1[-1])

                r2 = self.driver_mgr.driver.final()
                if r2[0] is False:
                    raise RuntimeError(r2[-1])
                else:
                    instance.log_info(r2[-1])

                # 仅通知，不退出
                if not auto_exit:
                    if not self.disable_unnecessary_notify:
                        if self.em:
                            old_subj = self.em.get_subject()
                            self.em.update_subject("成功-{}".format(old_subj))
                            self.em.quick_send("{}\n取数完毕，请检查".format(desc))
                        else:
                            print("成功-{}".format(notify_object))
                            print("{}\n取数完毕，请检查".format(desc))
                    return True

                instance.dispose("取数完毕，程序关闭中")
                if not self.disable_unnecessary_notify:
                    if self.em:
                        old_subj = self.em.get_subject()
                        self.em.update_subject(f"成功-{old_subj}")
                        self.em.quick_send("{}\n取数完毕，请检查".format(desc))
                    else:
                        print(f"成功-{notify_object}")
                        print("{}\n取数完毕，请检查".format(desc))
                return True

            except Exception as e:
                # 截图
                path = '{}{}error_{}.png'.format(self.sc_loc, os.sep, int(datetime.datetime.now().timestamp()))
                self.hosted_instance.brow.save_screenshot(path)
                self.hosted_instance.log_info("截图已保存到{}".format(path))

                instance.log_error("报错：{}".format(e))
                instance.log_error(traceback.format_exc())

                # 仅通知，不退出
                if not auto_exit:
                    if self.em:
                        old_subj = self.em.get_subject()
                        self.em.update_subject(f"失败-{old_subj}")
                        self.em.quick_send("取数崩溃：{}\n{}".format(e, traceback.format_exc()))
                    else:
                        print(f"失败-{notify_object}")
                        print("取数崩溃：{}\n{}".format(e, traceback.format_exc()))

                    return False

                instance.dispose("程序崩溃，立即退出")
                if self.em:
                    old_subj = self.em.get_subject()
                    self.em.update_subject(f"失败-{old_subj}")
                    self.em.quick_send("取数崩溃：{}\n{}".format(e, traceback.format_exc()))
                else:
                    print(f"失败-{notify_object}")
                    print("取数崩溃：{}\n{}".format(e, traceback.format_exc()))
                return False
