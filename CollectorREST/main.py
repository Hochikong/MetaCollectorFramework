# -*- coding: utf-8 -*-
# @Time    : 2024/9/8 3:51
# @Author  : Hochikong
# @FileName: server.py

from fastapi import FastAPI

from CollectorREST.database import engine
from CollectorREST.entities import db_entity
from CollectorREST.routers import tasks

db_entity.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
