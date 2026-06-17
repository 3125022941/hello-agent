# models.py

from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    # 系统生成的唯一 id
    id: str

    # 原始信号
    signal: str

    # 信号来源，可选
    source: Optional[str] = None

    # 补充备注，可选
    note: Optional[str] = None


class Observation(BaseModel):
    # observation 自己的 id
    id: str

    # 这个 observation 来自哪个 event
    event_id: str

    # 对原始信号的简单总结
    summary: str

    # 保存原始 signal，方便追溯
    raw_signal: str


class Task(BaseModel):
    # task 自己的 id
    id: str

    # 这个 task 来自哪个 observation
    observation_id: str

    # 任务标题
    title: str

    # 任务状态，比如 todo / done
    status: str