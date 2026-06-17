# schemas.py

from typing import Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    # 用户创建 event 时，必须传 signal。
    # 例如："用户最近频繁关注 AI Agent"
    signal: str

    # source 是可选字段，用来说明这个信号来自哪里。
    # 例如："obsidian"、"chat"、"browser"
    source: Optional[str] = None

    # note 也是可选字段，用来补充说明。
    note: Optional[str] = None


class ObservationCreate(BaseModel):
    # 提取 observation 时，需要告诉系统：基于哪个 event 提取。
    events_id: str


class TaskCreate(BaseModel):
    # 生成 task 时，需要告诉系统：基于哪个 observation 生成。
    observations_id: str