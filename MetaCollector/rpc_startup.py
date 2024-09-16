import argparse
import subprocess
import sys
import traceback
import psutil
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

from loguru import logger
from MetaCollector.base.utils.selenium.factory import yaml_loader
from MetaCollector.base.utils.ind_logger.report import beauty_dict_report
from MetaCollector.crawler.agent import CollectAgent


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class AgentWrapper(object):
    def __init__(self, logger: any, args: argparse.Namespace):
        self._args = args
        self.logger = logger
        self.cfg_content = yaml_loader(args.cfg)
        # noVNC forward process
        self.proc = None
        self.xvfb_launch = False
        self.agent = CollectAgent()

        agent = self.agent
        print("加载配置文件中...")
        if args.notify:
            agent.load_cfg_from_files(args.cfg, args.notify, args.debug)
        else:
            agent.load_cfg_from_files(args.cfg, debug_mode=args.debug)

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

    def goto_rebot_check(self):
        agent = self.agent
        agent.hosted_instance.brow.get("https://nowsecure.nl")

    def goto_url(self, url: str):
        agent = self.agent
        agent.hosted_instance.brow.get(url)

    def launch_remote_chrome(self, command: str):
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

    def run_driver(self, command: str, cfg_input: dict = None):
        agent = self.agent
        logger = self.logger

        if cfg_input is None:
            cfg_input = self.cfg_content

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


def cli_launch():
    parser = argparse.ArgumentParser("MCFDataCollector Modular Scraper XMLRPC Server")
    add_basic_parser(parser)
    args = parser.parse_args()

    DEFAULT_BIND_IP = '0.0.0.0'
    DEFAULT_PORT = 5100

    if args.bind:
        DEFAULT_BIND_IP = args.bind
    if args.port:
        DEFAULT_PORT = args.port

    inst = AgentWrapper(logger, args)
    try:
        with ThreadXMLRPCServer((DEFAULT_BIND_IP, DEFAULT_PORT)) as server:
            server.register_introspection_functions()
            server.register_instance(inst)

            logger.info("\n")
            logger.info("*** MCFDataCollector Modular Scraper XMLRPC Server launch done ***")
            logger.info("*** Listen On {}:{} ***".format(DEFAULT_BIND_IP, DEFAULT_PORT))
            server.serve_forever()
    except KeyboardInterrupt:
        logger.info("*** MCFDataCollector Modular Scraper XMLRPC Server closing... ***\n")
        sys.exit(0)


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
    # RPC版本只支持自由模式
    # parser.add_argument('--free', help="启用自由模式，不执行任何操作，仅启动浏览器", action='store_true')
    parser.add_argument('--all_notify', help="启用全部通知", action='store_true')
    parser.add_argument('-b', '--bind',
                        type=str, help="监听ip", metavar="默认为0.0.0.0")
    parser.add_argument('-p', '--port',
                        type=int, help="监听端口", metavar="默认为5100")
    parser.add_argument('-l', '--log',
                        type=str, help="指定日志存储prefix，如无指定，则在当前目录输出日志")


if __name__ == '__main__':
    cli_launch()
