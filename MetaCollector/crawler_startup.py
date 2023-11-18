import argparse
import subprocess
import traceback

import psutil

from MetaCollector.base.utils.ind_logger.report import beauty_dict_report
from MetaCollector.base.utils.selenium.factory import yaml_loader
from MetaCollector.crawler.agent import CollectAgent


def cli_launch():
    parser = argparse.ArgumentParser("MCFDataCollector Modular Scraper")
    add_basic_parser(parser)
    args = parser.parse_args()

    # noVNC forward process
    proc = None

    agent = CollectAgent()
    print("加载配置文件中...")
    if args.notify:
        agent.load_cfg_from_files(args.cfg, args.notify, args.debug)
    else:
        agent.load_cfg_from_files(args.cfg, debug_mode=args.debug)

    if args.all_notify:
        agent.enable_all_notify()

    xvfb_launch = False
    if args.xdisplay:
        # 启动vnc转发服务的两种途径
        if agent.yaml_cfg['selenium'].get('forward_port', -1) != -1:
            if agent.yaml_cfg['selenium'].get('xdisplay_backend', '') == 'xvnc':
                source_port = agent.yaml_cfg['selenium']['xdisplay_port']
                proc = subprocess.Popen(
                    f"novnc --listen {int(agent.yaml_cfg['selenium'].get('forward_port'))} --vnc localhost:{source_port}",
                    shell=True)
            xvfb_launch = agent.enable_xvfb()

        elif args.forward:
            if agent.yaml_cfg['selenium'].get('xdisplay_backend', '') == 'xvnc':
                source_port = agent.yaml_cfg['selenium']['xdisplay_port']
                target_port = int(args.forward)
                proc = subprocess.Popen(f"novnc --listen {target_port} --vnc localhost:{source_port}", shell=True)
            xvfb_launch = agent.enable_xvfb()
        else:
            xvfb_launch = agent.enable_xvfb()

    if args.free:
        print("Enter '/h' to get more information")
        while True:
            iv = input("MCFDataCollector|FreeMode#>")
            if iv == '/q':
                if xvfb_launch:
                    agent.stop_xvfb()

                    if proc is not None:
                        pid = proc.pid
                        parent = psutil.Process(pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        proc.terminate()
                agent.dispose()
                break
            elif iv == '/sc':
                agent.hosted_instance.brow.get("https://nowsecure.nl")
            elif iv == '/h':
                print("""
                /q - quit
                /h - help
                /sc - safe check
                /login - just login
                /ls - list all drivers
                /get - goto url, example: /get;https://xxx.com
                /run - run driver, example: /run;NAMESPACE:DRIVER
                /remote - create a remote debug chrome, example: /remote;PORT "USER_DATA_DIR" e.g. /remote;9223 "D:\\selenium_workspace\\remote_ud"
                                                                 /remote;ls  
                                                                 /remote;kill PORT
                """)
            elif iv == '/ls':
                print("")
            elif iv.startswith('/remote'):
                if iv.split(';')[-1] == 'ls':
                    print(list(agent.browser_holder.cmd_procs.keys()))
                elif iv.split(';')[-1].startswith('kill'):
                    try:
                        port = int(iv.split(';')[-1].split(' ')[-1])
                        for cmd in list(agent.browser_holder.cmd_procs.keys()):
                            if str(port) in cmd:
                                agent.browser_holder.kill_browser(cmd)
                    except ValueError:
                        print("Port error can't parse to int")
                    except Exception:
                        print(traceback.format_exc())
                else:
                    try:
                        port = int(iv.split(';')[-1].split(' ')[0])
                        ud_path = iv.split(';')[-1].split(' ')[-1]
                        agent.browser_holder.get_browser(agent.chrome_path, port, ud_path)
                    except ValueError:
                        print("Port error can't parse to int")
                    except Exception:
                        print(traceback.format_exc())
            elif iv.startswith('/get'):
                agent.hosted_instance.brow.get(iv.replace("/get;", "").strip())
            elif iv.startswith('/run'):
                print("启动chrome")
                agent.launch_for_drivers()

                ns_dr = iv.split(";")[-1]
                ns = ns_dr.split(":")[0]
                dr = ns_dr.split(":")[1]

                run_results = {}

                agent.load_driver(ns, dr)
                print(f"驱动{dr}已加载完毕")
                print("运行驱动：{}".format(dr))
                r = agent.run_extension(dr, agent.hosted_instance, yaml_loader(args.cfg), auto_exit=False, range=False)
                run_results[dr] = (r, agent.plugin_run_desc)

                if agent.em:
                    agent.em.update_subject("run已执行全部模块")
                    agent.em.quick_send(f"取数任务完成, 统计报告如下：\n\n{beauty_dict_report(run_results)}")
                else:
                    print("run已执行全部模块")
                    print(f"取数任务完成, 统计报告如下：\n\n{beauty_dict_report(run_results)}")
            else:
                print("不被支持的指令")

    else:
        if args.debug != 'yes':
            agent.hosted_instance.brow.set_window_size(2560, 1080)

        print("加载驱动中")
        agent.load_driver(args.driver, args.driver)

        print("运行驱动：{}".format(args.driver))

        cfg_d = agent.yaml_cfg
        if args.range:
            agent.run_extension(args.driver, agent.hosted_instance, cfg_d, auto_exit=False, range=True)
        else:
            agent.run_extension(args.driver, agent.hosted_instance, cfg_d, auto_exit=False, range=False)

        if xvfb_launch:
            agent.stop_xvfb()

    if proc is not None:
        proc.terminate()
    agent.dispose()


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
    parser.add_argument('-x', '--xdisplay',
                        help="是否启用headless模式，仅支持在linux下运行，可以配置文件中选择基于Xvfb或者VNC的后端",
                        action='store_true')
    parser.add_argument('-f', '--forward', help="通过noVNC转发本地xdisplay到浏览器", metavar="用于被外部访问的目标端口",
                        type=int)
    parser.add_argument('--free', help="启用自由模式，不执行任何操作，仅启动浏览器", action='store_true')
    parser.add_argument('--all_notify', help="启用全部通知", action='store_true')
