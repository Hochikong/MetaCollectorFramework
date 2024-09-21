import logging
from .services import task_queue_maintainer
from .services import mcf_mgmt
from .app_config import MCF_CONFIG, TASK_TEMPLATE_CONFIG

logger = logging.getLogger('main_app')

agent_service = mcf_mgmt.AgentFactoryWrapper()

queue_maintainer = task_queue_maintainer.TaskQueueMaintainer(logger=logger)


def get_queue_maintainer():
    return queue_maintainer


def get_agent_service():
    return agent_service


def get_mcf_config_path():
    return MCF_CONFIG, TASK_TEMPLATE_CONFIG
