# main.py

from fastapi import FastAPI, HTTPException

from models import Event, Observation, Task
from schemas import EventCreate, ObservationCreate, TaskCreate
from services import create_event, extract_observation, generate_task
from storage import events, observations, tasks


app = FastAPI(title="learning-observer-api", version="0.2")


# 创建事件接口
# 方法：POST
# 路径：/events
# 请求体：EventCreate，也就是用户传进来的 signal/source/note
# 返回体：Event，也就是系统生成 id 后的完整事件
@app.post("/events", response_model=Event)
def create_event_api(event: EventCreate):
    # 路由层只负责接收 HTTP 请求。
    # 真正“创建事件”的逻辑交给 services.py 里的 create_event。
    return create_event(event)


# 查看所有事件接口
# 方法：GET
# 路径：/events
# 请求体：没有
# 作用：返回当前内存里保存的所有 events
@app.get("/events")
def list_events():
    return {
        # items 是事件列表本身。
        "items": events,

        # count 是事件数量。
        "count": len(events),
    }


# 提取观察接口
# 方法：POST
# 路径：/observations/extract
# 请求体：ObservationCreate，里面包含 events_id
# 作用：根据某个 event 的 id，生成一条 observation
# 返回体：Observation
@app.post("/observations/extract", response_model=Observation)
def extract_observation_api(data: ObservationCreate):
    # 调用业务逻辑：根据 event_id 提取 observation。
    # data.events_id 来自用户请求体。
    observation = extract_observation(data.events_id)

    # services.py 返回 None，说明没找到 event。
    # main.py 把这个业务结果转换成 HTTP 404。
    if observation is None:
        raise HTTPException(status_code=404, detail="event not found")

    return observation


# 查看所有观察接口
# 方法：GET
# 路径：/observations
# 请求体：没有
# 作用：返回当前内存里保存的所有 observations
@app.get("/observations")
def list_observations():
    return {
        # items 是观察列表本身。
        "items": observations,

        # count 是观察数量，方便前端或调用者快速知道有多少条。
        "count": len(observations),
    }


# 生成任务接口
# 方法：POST
# 路径：/tasks/generate
# 请求体：TaskCreate，里面包含 observations_id
# 作用：根据某个 observation 的 id，生成一条 task
# 返回体：Task
@app.post("/tasks/generate", response_model=Task)
def generate_task_api(data: TaskCreate):
    # 调用业务逻辑：根据 observation_id 生成 task。
    # data.observations_id 来自用户请求体。
    task = generate_task(data.observations_id)

    # 如果 services.py 返回 None，说明没有找到对应 observation。
    # 这里转换成 HTTP 404，告诉调用者资源不存在。
    if task is None:
        raise HTTPException(status_code=404, detail="observation not found")

    return task


# 查看所有任务接口
# 方法：GET
# 路径：/tasks
# 请求体：没有
# 作用：返回当前内存里保存的所有 tasks
@app.get("/tasks")
def list_tasks():
    return {
        # items 是任务列表本身。
        "items": tasks,

        # count 是任务数量。
        "count": len(tasks),
    }
