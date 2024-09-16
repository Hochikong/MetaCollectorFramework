import logging
from .services import task_queue_maintainer
logger = logging.getLogger('main_app')

queue_maintainer = task_queue_maintainer.TaskQueueMaintainer(logger=logger)
queue_maintainer.load_pending_tasks_from_db()


def get_queue_maintainer():
    return queue_maintainer
