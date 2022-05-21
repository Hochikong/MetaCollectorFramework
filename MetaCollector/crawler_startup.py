import argparse
import subprocess
from time import sleep

import psutil

from MetaCollector.base.utils.ind_logger.report import beauty_dict_report
from MetaCollector.crawler.agent import CollectAgent


def cli_launch():
    parser = argparse.ArgumentParser("MCFDataCollector Modular Scraper")
    add_basic_parser(parser)
    args = parser.parse_args()

    # noVNC forward process
    proc = None

    worker = CollectAgent()
    print("加载配置文件中...")
    worker.load_cfg_from_files(args.cfg, args.notify, args.debug)

    if args.all_notify:
        worker.enable_all_notify()

    xvfb_launch = False
    if args.xdisplay:
        # 启动vnc转发服务的两种途径
        if worker.yaml_cfg['selenium'].get('forward_port', -1) != -1:
            if worker.yaml_cfg['selenium'].get('xdisplay_backend', '') == 'xvnc':
                source_port = worker.yaml_cfg['selenium']['xdisplay_port']
                proc = subprocess.Popen(
                    f"novnc --listen {int(worker.yaml_cfg['selenium'].get('forward_port'))} --vnc localhost:{source_port}",
                    shell=True)
            xvfb_launch = worker.enable_xvfb()

        elif args.forward:
            if worker.yaml_cfg['selenium'].get('xdisplay_backend', '') == 'xvnc':
                source_port = worker.yaml_cfg['selenium']['xdisplay_port']
                target_port = int(args.forward)
                proc = subprocess.Popen(f"novnc --listen {target_port} --vnc localhost:{source_port}", shell=True)
            xvfb_launch = worker.enable_xvfb()
        else:
            xvfb_launch = worker.enable_xvfb()

    print("启动chrome")
    worker.launch_for_drivers()

    if args.free:
        print("Enter '/h' to get more information")
        while True:
            iv = input("MCFDataCollector|FreeMode#>")
            if iv == '/q':
                if xvfb_launch:
                    worker.stop_xvfb()

                    if proc is not None:
                        pid = proc.pid
                        parent = psutil.Process(pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        proc.terminate()
                break
            elif iv == '/sc':
                worker.hosted_instance.brow.get("https://nowsecure.nl")
            elif iv == '/h':
                print("""
                /q - quit
                /h - help
                /sc - safe check
                /r_run - should login first. range run modules with continue mode, command example: r_run:xxx
                /run - should login first. run modules with continue mode on latest day, command example: run:xxx
                /login - just login
                /ls - list all drivers
                """)
            elif iv == '/ls':
                print("")
            elif iv.startswith('/r_run'):
                command_split = iv.split(":")[-1]
                run_modules = [i.strip() for i in command_split.split(",")]

                run_results = {}

                for d in run_modules:
                    worker.load_driver(d)
                    worker.set_continue_mode_for_driver(True)
                    print(f"驱动{d}已加载完毕")
                    print("运行驱动：{}".format(d))
                    r = worker.run_extension(d, worker.hosted_instance, 'f', args.cfg, auto_exit=False, range=True,
                                             email_cfg=worker.email_cfg)
                    sleep(10)
                    run_results[d] = (r, worker.plugin_run_desc)

                worker.em.update_subject("r_run已执行全部模块")
                worker.em.quick_send(f"取数任务完成, 统计报告如下：\n\n{beauty_dict_report(run_results)}")
            elif iv.startswith('/run'):
                command_split = iv.split(":")[-1]
                run_modules = [i.strip() for i in command_split.split(",")]

                run_results = {}

                for d in run_modules:
                    worker.load_driver(d)
                    worker.set_continue_mode_for_driver(True)
                    print(f"驱动{d}已加载完毕")
                    print("运行驱动：{}".format(d))
                    r = worker.run_extension(d, worker.hosted_instance, 'f', args.cfg, auto_exit=False, range=False,
                                             email_cfg=worker.email_cfg)
                    sleep(10)
                    run_results[d] = (r, worker.plugin_run_desc)

                worker.em.update_subject("run已执行全部模块")
                worker.em.quick_send(f"取数任务完成, 统计报告如下：\n\n{beauty_dict_report(run_results)}")
            else:
                print("不被支持的指令")

    else:
        if args.debug != 'yes':
            worker.hosted_instance.brow.set_window_size(2560, 1080)

        print("加载驱动中")
        worker.load_driver(args.driver)

        print("运行驱动：{}".format(args.driver))

        if args.range:
            worker.run_extension(args.driver, worker.hosted_instance, 'f', args.cfg, auto_exit=True, range=True,
                                 email_cfg=worker.email_cfg)
        else:
            worker.run_extension(args.driver, worker.hosted_instance, 'f', args.cfg, auto_exit=True, range=False,
                                 email_cfg=worker.email_cfg)

        if xvfb_launch:
            worker.stop_xvfb()

    if proc is not None:
        proc.terminate()


def add_basic_parser(parser):
    parser.add_argument('-c', '--cfg',
                        type=str, help="Configuration file path.", metavar="YAML FILE")
    parser.add_argument('-d', '--debug',
                        type=str, help="If 'yes', enable debug mode, else headless mode", metavar="yes or no")
    parser.add_argument('-n', '--notify',
                        type=str, help="从配置文件读取邮件通知服务的配置信息", metavar="文件路径")
    parser.add_argument('-D', '--driver',
                        type=str, help="加载哪个驱动", metavar="驱动名")
    parser.add_argument('-r', '--range', help="历史取数模式，指定范围进行取数", action='store_true')
    parser.add_argument('-x', '--xdisplay', help="是否启用headless模式，仅支持在linux下运行，可以配置文件中选择基于Xvfb或者VNC的后端",
                        action='store_true')
    parser.add_argument('-f', '--forward', help="通过noVNC转发本地xdisplay到浏览器", metavar="用于被外部访问的目标端口", type=int)
    parser.add_argument('--free', help="启用自由模式，不执行任何操作，仅启动浏览器", action='store_true')
    parser.add_argument('--all_notify', help="启用全部通知", action='store_true')
