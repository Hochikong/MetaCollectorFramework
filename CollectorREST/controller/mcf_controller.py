import traceback
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from ..domains.mcf import ArgsReceive, RuntimeStorageTaskReceive, MgmtCommand
from ..dependencies import get_queue_maintainer, get_agent_service
from ..repository import basic_crud_repository
from ..database import SessionLocal
from ..services.mcf_mgmt import AgentFactoryWrapper, Args

router = APIRouter()


@router.get("/mcf/status/{task_uid}", tags=['mcf_mgmt'])
def receive_task(task_uid: str, mcf_service: AgentFactoryWrapper = Depends(get_agent_service)):
    try:
        task_info: dict = mcf_service.rs.current_tasks[task_uid]
        return task_info
    except Exception:
        raise HTTPException(status_code=404, detail=traceback.format_exc())


@router.get("/mcf/instances/", tags=['mcf_mgmt'])
def receive_task(task_uid: str, mcf_service: AgentFactoryWrapper = Depends(get_agent_service)):
    try:
        instances = {'instances': mcf_service.rs.agents_scope.keys()}
        return instances
    except Exception:
        raise HTTPException(status_code=404, detail=traceback.format_exc())


@router.post("/mcf/create/", tags=['mcf_mgmt'])
def receive_task(task: ArgsReceive, mcf_service: AgentFactoryWrapper = Depends(get_agent_service)):
    task_id = mcf_service.create_agent('system', Args.from_dict(task.to_dict()))
    return task_id


@router.post("/mcf/stop/{instance_id}", tags=['mcf_mgmt'])
def receive_task(instance_id: str, mcf_service: AgentFactoryWrapper = Depends(get_agent_service)):
    try:
        task_id = mcf_service.stop_agent('system', instance_id)
        return task_id
    except Exception:
        raise HTTPException(status_code=404, detail=traceback.format_exc())


@router.post("/mcf/launch_chrome/{instance_id}", tags=['mcf_mgmt'])
def receive_task(instance_id: str, cmd: MgmtCommand, mcf_service: AgentFactoryWrapper = Depends(get_agent_service)):
    try:
        task_id = mcf_service.launch_remote_chrome('system', instance_id, cmd.cmd)
        return task_id
    except Exception:
        raise HTTPException(status_code=404, detail=traceback.format_exc())


@router.post("/mcf/run_driver/{instance_id}", tags=['mcf_mgmt'])
def receive_task(instance_id: str, cmd: MgmtCommand, mcf_service: AgentFactoryWrapper = Depends(get_agent_service)):
    try:
        task_id = mcf_service.run_driver('system', instance_id, cmd.cmd, cmd.cfg_input)
        return task_id
    except Exception:
        raise HTTPException(status_code=404, detail=traceback.format_exc())