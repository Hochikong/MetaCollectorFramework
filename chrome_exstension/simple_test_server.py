# -*- coding: utf-8 -*-
# @Time    : 2024/8/6 23:47
# @Author  : Hochikong
# @FileName: simple_test_server.py
from fastapi import FastAPI
from typing import Dict, Any
app = FastAPI()


@app.post("/tasks/single/")
def receive_post(request: Dict[Any, Any]):
    print(request)
    return {"message": "Data received successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
