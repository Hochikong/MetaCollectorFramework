import logging
from .services import task_queue_maintainer
from .services import mcf_mgmt

logger = logging.getLogger('main_app')

agent_service = mcf_mgmt.AgentFactoryWrapper()

queue_maintainer = task_queue_maintainer.TaskQueueMaintainer(logger=logger)
queue_maintainer.load_pending_tasks_from_db()


def get_queue_maintainer():
    return queue_maintainer


def get_agent_service():
    return agent_service
