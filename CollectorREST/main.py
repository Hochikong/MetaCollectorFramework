# -*- coding: utf-8 -*-
# @Time    : 2024/9/8 3:51
# @Author  : Hochikong
# @FileName: server.py
import logging
from fastapi import FastAPI, Depends

from .database import engine
from .entities import db_entity

# from uvicorn.server import logger
logger = logging.getLogger('main_app')
db_entity.Base.metadata.create_all(bind=engine)

from .controller import tasks_controller, mcf_controller
from .dependencies import get_queue_maintainer, get_agent_service

app = FastAPI(dependencies=[Depends(get_queue_maintainer), Depends(get_agent_service)])
app.include_router(tasks_controller.router)
app.include_router(mcf_controller.router)

queue_m = get_queue_maintainer()
logger.info("Queue Maintainer init done!")


@app.get("/")
def read_root():
    return {"Hello": "World"}
