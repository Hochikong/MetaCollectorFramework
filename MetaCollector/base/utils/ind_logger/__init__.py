from MetaCollector.base.utils.ind_logger.notify import NotificationHandlerNew
from loguru import logger


LOG_LEVEL_ENUM = ['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']


def add_logger_config(
        sink: any,
        level: str,
        module: str = '__main__',
        log_format: str = '[{time:YYYY-MM-DD} {time:HH:mm:ss}][{file}:{line}][{level}] -> {message}',
        rotation: str = '3 hours',
        retention: str = '10 days'
) -> int:
    """为全局的logger创建一个绑定当前__name__的日志处理器

    :param sink: 日志输出目标，可以是一个handler或者一个文件，根据类型切换
    :param level: 最低的日志级别
    :param module: logger绑定的代码模块
    :param log_format: 日志记录格式，例如"{time} - {level} - {message}"
    :param retention: 清理掉多少天之前的旧日志
    :param rotation: 何时进行日志滚动
    :return: 返回handler的id，用于被logger.remove()去移除指定id的handler
    """
    if level not in LOG_LEVEL_ENUM:
        return -1

    if isinstance(sink, str):
        sink_content = "%s_{time}.log" % sink
        return logger.add(sink=sink_content,
                          level=level,
                          format=log_format,
                          filter=module,
                          colorize=None,
                          backtrace=True,
                          diagnose=True,
                          encoding='utf-8',
                          rotation=rotation,
                          retention=retention,
                          enqueue=True)
    elif isinstance(sink, NotificationHandlerNew):
        sink_content = sink
        return logger.add(sink=sink_content,
                          level=level,
                          filter=module,
                          colorize=None,
                          backtrace=True,
                          diagnose=True,
                          enqueue=True)
    else:
        raise NotImplementedError("尚不支持类型为{}的sink".format(type(sink)))
