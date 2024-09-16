# -*- coding: utf-8 -*-
# @Time    : 2024/9/8 3:51
# @Author  : Hochikong
# @FileName: server.py
import logging
from fastapi import FastAPI

from .database import engine
from .entities import db_entity
from .controller import tasks_controller
from .services import task_queue_maintainer
# from uvicorn.server import logger
logger = logging.getLogger('main_app')
db_entity.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(tasks_controller.router)

queue_maintainer = task_queue_maintainer.TaskQueueMaintainer(logger=logger)
queue_maintainer.load_pending_tasks_from_db()


@app.get("/")
def read_root():
    return queue_maintainer.queue.qsize()
