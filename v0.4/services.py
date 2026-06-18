# services.py
#
# 这个文件负责“业务逻辑”。
#
# v0.2 的 services.py 是操作内存列表：
#
# events.append(...)
# observations.append(...)
# tasks.append(...)
#
# v0.3 开始接 SQLite 后，不再直接操作 Python 列表。
# 所有数据都要通过数据库 session 来读写。
#
# 简单理解：
#
# session = 一次数据库操作窗口
#
# 你要新增数据、查询数据、保存数据，都要通过 session。
#
# main.py 负责从 FastAPI 拿到 session。
# services.py 负责用这个 session 做真正的业务处理。

from uuid import uuid4

from sqlmodel import Session, select

from models import Event, Observation, Task
from schemas import EventCreate,ReviewCreate
from models import Event, Observation, Task, Review

def create_event(event: EventCreate, session: Session):
    # 创建一个 Event 数据库对象。
    #
    # 注意：
    # 这里不再创建普通 dict。
    #
    # v0.2 是：
    # new_event = {"id": "...", "signal": "..."}
    #
    # v0.3 是：
    # db_event = Event(id="...", signal="...")
    #
    # 因为 Event 现在是 SQLModel 表模型，
    # 它既是 Python 对象，也能被保存进 SQLite 数据库。
    db_event = Event(
        id=str(uuid4()),
        signal=event.signal,
        source=event.source,
        note=event.note,
    )

    # 把这个对象加入数据库 session。
    #
    # 这一步只是告诉 session：
    # “我准备新增这条数据。”
    #
    # 注意：这一步还没有真正写入数据库文件。
    session.add(db_event)

    # 提交事务。
    #
    # commit 之后，数据才会真正写入 SQLite。
    session.commit()

    # 刷新对象。
    #
    # refresh 会从数据库重新读取这条记录，
    # 确保返回给 API 的对象是数据库保存后的最新状态。
    session.refresh(db_event)

    # 返回新创建的事件。
    #
    # FastAPI 会根据 response_model 把它转成 JSON。
    return db_event


def list_events(session: Session):
    # 查询所有 Event。
    #
    # select(Event) 的意思是：
    # 生成一条 SQL 查询，目标是 Event 对应的表。
    statement = select(Event)

    # session.exec(statement) 执行查询。
    #
    # .all() 表示取出所有结果，返回一个列表。
    return session.exec(statement).all()


def find_event(event_id: str, session: Session):
    # 根据主键 id 查询一条 Event。
    #
    # 因为 Event.id 是 primary_key，
    # 所以可以直接用 session.get(Event, event_id)。
    #
    # 如果找到了，返回 Event 对象。
    # 如果找不到，返回 None。
    return session.get(Event, event_id)


def extract_observation(event_id: str, session: Session):
    # 先根据 event_id 找到原始事件。
    #
    # 这里复用 find_event，
    # 避免把“怎么查 event”的逻辑重复写一遍。
    event = find_event(event_id, session)

    # 如果没有找到 event，说明用户传进来的 events_id 不存在。
    #
    # services.py 只返回 None。
    # 它不直接抛 HTTPException。
    #
    # 因为 HTTPException 属于 API 层的事情，
    # 应该交给 main.py 来处理。
    if event is None:
        return None

    # 创建一条 Observation 数据库对象。
    #
    # event_id 用来保存：
    # 这条 observation 是从哪条 event 生成的。
    #
    # raw_signal 保存原始 signal，
    # 方便后面查看 observation 时不用每次都回查 event。
    observation = Observation(
        id=str(uuid4()),
        event_id=event.id,
        summary=f"观察到信号：{event.signal}",
        raw_signal=event.signal,
    )

    # 保存 observation 到数据库。
    session.add(observation)
    session.commit()
    session.refresh(observation)

    return observation


def list_observations(session: Session):
    # 查询所有 Observation。
    statement = select(Observation)
    return session.exec(statement).all()


def find_observation(observation_id: str, session: Session):
    # 根据主键 id 查询一条 Observation。
    #
    # 找不到时返回 None。
    return session.get(Observation, observation_id)


def generate_task(observation_id: str, session: Session):
    # 先根据 observation_id 找到原始观察。
    observation = find_observation(observation_id, session)

    # 如果找不到 observation，说明用户传进来的 observations_id 不存在。
    #
    # 这里仍然只返回 None，
    # 让 main.py 决定怎么转换成 HTTP 404。
    if observation is None:
        return None

    # 创建一条 Task 数据库对象。
    #
    # observation_id 用来保存：
    # 这个任务是从哪条 observation 生成的。
    task = Task(
        id=str(uuid4()),
        observation_id=observation.id,
        title=f"基于观察生成任务：{observation.raw_signal}",
        status="todo",
    )

    # 保存 task 到数据库。
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def list_tasks(session: Session):
    # 查询所有 Task。
    statement = select(Task)
    return session.exec(statement).all()



def create_review(data: ReviewCreate, session: Session):
    # 先检查 task 是否存在。
    #
    # 因为 review 必须属于某一个 task。
    task = session.get(Task, data.task_id)

    # 如果 task 不存在，返回 None。
    # main.py 再把 None 转成 HTTP 404。
    if task is None:
        return None

    review = Review(
        id=str(uuid4()),
        task_id=data.task_id,
        summary=data.summary,
        score=data.score,
    )

    session.add(review)
    session.commit()
    session.refresh(review)

    return review

def list_reviews(session: Session):
    statement = select(Review)
    return session.exec(statement).all()