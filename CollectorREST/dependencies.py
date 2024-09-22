import logging
from .services import task_queue_maintainer
from .services import mcf_mgmt
from .services import main_mcf_holder
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


main_mcf = main_mcf_holder.MainMCF(get_agent_service(), get_queue_maintainer(), logger)


def get_main_mcf():
    return main_mcf
