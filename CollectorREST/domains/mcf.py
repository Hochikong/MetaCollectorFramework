from pydantic import BaseModel
from typing import Optional


class ArgsReceive(BaseModel):
    cfg: str
    debug: str
    notify: Optional[str] = None
    xdisplay: Optional[bool] = None
    forward: Optional[int] = None
    all_notify: Optional[bool] = None

    def to_dict(self):
        return {
            'cfg': self.cfg,
            'debug': self.debug,
            'notify': self.notify,
            'xdisplay': self.xdisplay,
            'forward': self.forward,
            'all_notify': self.all_notify,
        }


class RuntimeStorageTaskReceive(BaseModel):
    task: str
    instance_id: str
    instance_tag: str
    status: str
    start_time: str
    end_time: Optional[str]


class MgmtCommand(BaseModel):
    cmd: str
    cfg_input: Optional[str]
