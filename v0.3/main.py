# main.py
#
# 这个文件是 FastAPI 应用入口。
#
# main.py 只负责三件事：
#
# 1. 创建 FastAPI app
# 2. 注册 API 路由
# 3. 把 HTTP 请求交给 services.py 处理
#
# 到 v0.3 以后，数据已经不再保存在 storage.py 的内存列表里。
# 数据会写入 SQLite 数据库。
#
# 所以 main.py 需要多做一件事：
#
# 给每个接口注入数据库 session。
#
# session 从 database.py 里的 get_session() 来。

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from database import create_db_and_tables, get_session
from models import Event, Observation, Task
from schemas import EventCreate, ObservationCreate, TaskCreate
from services import (
    create_event,
    extract_observation,
    generate_task,
    list_events,
    list_observations,
    list_tasks,
)


app = FastAPI(title="learning-observer-api", version="0.3")


@app.on_event("startup")
def on_startup():
    # FastAPI 应用启动时会执行这个函数。
    #
    # create_db_and_tables() 会根据 models.py 里 table=True 的模型创建表。
    #
    # 例如：
    # Event       -> event 表
    # Observation -> observation 表
    # Task        -> task 表
    #
    # 如果表已经存在，不会重复创建。
    create_db_and_tables()


# 健康检查接口
# 方法：GET
# 路径：/health
# 请求体：没有
# 作用：确认服务是否正常启动
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "learning-observer-api",
        "version": "0.3",
    }


# 创建事件接口
# 方法：POST
# 路径：/events
# 请求体：EventCreate，也就是用户传进来的 signal/source/note
# 返回体：Event，也就是系统生成 id 后保存到数据库里的完整事件
@app.post("/events", response_model=Event)
def create_event_api(
    event: EventCreate,
    session: Session = Depends(get_session),
):
    # event 来自用户请求体。
    #
    # session 来自 FastAPI 的依赖注入：
    # Depends(get_session) 会调用 database.py 里的 get_session()。
    #
    # main.py 不直接写数据库逻辑。
    # 它只把 event 和 session 交给 services.py。
    return create_event(event, session)


# 查看所有事件接口
# 方法：GET
# 路径：/events
# 请求体：没有
# 作用：从 SQLite 查询所有 events
@app.get("/events")
def list_events_api(session: Session = Depends(get_session)):
    # list_events(session) 会去数据库里查询 Event 表。
    items = list_events(session)

    return {
        # items 是事件列表。
        "items": items,

        # count 是事件数量。
        "count": len(items),
    }


# 提取观察接口
# 方法：POST
# 路径：/observations/extract
# 请求体：ObservationCreate，里面包含 events_id
# 作用：根据某个 event 的 id，生成一条 observation
# 返回体：Observation
@app.post("/observations/extract", response_model=Observation)
def extract_observation_api(
    data: ObservationCreate,
    session: Session = Depends(get_session),
):
    # data.events_id 来自用户请求体。
    #
    # extract_observation 会先去数据库查 event。
    # 如果 event 存在，就创建 observation。
    # 如果 event 不存在，就返回 None。
    observation = extract_observation(data.events_id, session)

    # services.py 返回 None，说明没找到 event。
    #
    # main.py 把这个业务结果转换成 HTTP 404。
    # 这就是“业务层不关心 HTTP，路由层处理 HTTP”的分工。
    if observation is None:
        raise HTTPException(status_code=404, detail="event not found")

    return observation


# 查看所有观察接口
# 方法：GET
# 路径：/observations
# 请求体：没有
# 作用：从 SQLite 查询所有 observations
@app.get("/observations")
def list_observations_api(session: Session = Depends(get_session)):
    items = list_observations(session)

    return {
        # items 是观察列表。
        "items": items,

        # count 是观察数量。
        "count": len(items),
    }


# 生成任务接口
# 方法：POST
# 路径：/tasks/generate
# 请求体：TaskCreate，里面包含 observations_id
# 作用：根据某个 observation 的 id，生成一条 task
# 返回体：Task
@app.post("/tasks/generate", response_model=Task)
def generate_task_api(
    data: TaskCreate,
    session: Session = Depends(get_session),
):
    # data.observations_id 来自用户请求体。
    #
    # generate_task 会先去数据库查 observation。
    # 如果 observation 存在，就创建 task。
    # 如果 observation 不存在，就返回 None。
    task = generate_task(data.observations_id, session)

    # 如果 services.py 返回 None，说明没有找到对应 observation。
    if task is None:
        raise HTTPException(status_code=404, detail="observation not found")

    return task


# 查看所有任务接口
# 方法：GET
# 路径：/tasks
# 请求体：没有
# 作用：从 SQLite 查询所有 tasks
@app.get("/tasks")
def list_tasks_api(session: Session = Depends(get_session)):
    items = list_tasks(session)

    return {
        # items 是任务列表。
        "items": items,

        # count 是任务数量。
        "count": len(items),
    }
