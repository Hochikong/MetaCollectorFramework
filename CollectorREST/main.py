# -*- coding: utf-8 -*-
# @Time    : 2024/9/8 3:51
# @Author  : Hochikong
# @FileName: server.py

from typing import Union

from fastapi import FastAPI

from CollectorREST.routers import tasks

app = FastAPI()
app.include_router(tasks.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
