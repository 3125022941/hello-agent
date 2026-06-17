from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException

# 创建 fastapi 应用对象
app = FastAPI(title="learning-observer-api", version="0.1")

# 三个列表当临时数据库
events = []  # 事件
observations = []  # 观察
tasks = []  # 任务
# 注意只保存在内存里，服务重启就会消失

# 定义接口的请求体
class EvenCreate(BaseModel):
    signal: str  # 事件信号，类型字符串
    source: Optional[str] = None  # 来源
    note: Optional[str] = None


class ObservationCreate(BaseModel):
    events_id: str


class TaskCreate(BaseModel):
    observations_id: str


class Event(BaseModel):
    id: str
    signal: str
    source: Optional[str] = None
    note: Optional[str] = None


class Observation(BaseModel):
    id: str
    event_id: str
    summary: str
    raw_signal: str


class Task(BaseModel):
    id: str
    observation_id: str
    title: str
    status: str


# 定义一个 get 接口
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "learning-observer-api",
        "version": "0.1",
    }


# 定义一个 post 接口，用于创建事件
# 一条事件：agent 观察到的原始信号
@app.post("/events", response_model=Event)
def create_event(event: EvenCreate):
    new_event = {
        "id": str(uuid4()),
        "signal": event.signal,  # 请求里的 signal 放进去
        "source": event.source,  # 请求里的 source 存进去
        "note": event.note,
    }
    events.append(new_event)
    return new_event


# 定义 post 接口，根据某个 event 提取 observation
# 根据事件 id 提取：用户最近频繁关注 agent
# 观察到信号：用户最近频繁关注 AI Agent
@app.post("/observations/extract", response_model=Observation)
def extract_observation(data: ObservationCreate):
    event = None
    for item in events:  # 遍历所有的 events
        if item["id"] == data.events_id:  # 判断当前 event 的 id 是否等于用户传进来的 events_id
            event = item  # 找到了返回该事件，没找到返回 None
            break
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")

    observation = {
        "id": str(uuid4()),
        "event_id": event["id"],
        "summary": f"观察到信号：{event['signal']}",
        "raw_signal": event["signal"],
    }
    observations.append(observation)
    return observation


# 依据某个 observation 生成 task
# 请求体必须包括某个观察 id
@app.post("/tasks/generate", response_model=Task)
def generate_task(data: TaskCreate):
    observation = None
    for item in observations:
        if item["id"] == data.observations_id:
            observation = item
            break
    if observation is None:
        raise HTTPException(status_code=404, detail="observation not found")

    task = {
        "id": str(uuid4()),
        "observation_id": observation["id"],  # 生成任务 id
        "title": f"基于观察生成任务：{observation['raw_signal']}",  # 记录这个任务来自哪个观察
        "status": "todo",
    }
    tasks.append(task)  # 把任务保存到 tasks 列表
    return task  # 返回新生成的任务


# 定义 get 接口，用于查看所有任务
@app.get("/tasks")
def list_tasks():
    return {
        "items": tasks,  # 所有任务列表
        "count": len(tasks),  # 任务数量
    }


@app.get("/events")
def list_events():
    return {
        "items": events,
        "count": len(events),
    }


@app.get("/observations")
def list_observations():
    return {
        "items": observations,
        "count": len(observations),
    }
