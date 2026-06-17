# services.py

from uuid import uuid4

from schemas import EventCreate
from storage import events, observations, tasks


def create_event(event: EventCreate):
    # 创建一个新的 event 字典。
    # id 由系统生成，signal/source/note 来自用户请求。
    new_event = {
        "id": str(uuid4()),
        "signal": event.signal,
        "source": event.source,
        "note": event.note,
    }

    # 保存到临时数据库 events 里。
    events.append(new_event)

    # 返回新创建的 event。
    return new_event


def find_event(event_id: str):
    # 在所有 events 里查找指定 id 的 event。
    for item in events:
        if item["id"] == event_id:
            return item

    # 找不到就返回 None。
    return None

def extract_observation(event_id: str):
    # 先根据 event_id 找到原始 event。
    event = find_event(event_id)

    # 如果找不到 event，先返回 None。
    # HTTP 404 不在这里处理，交给 main.py 处理。
    if event is None:
        return None

    observation = {
        "id": str(uuid4()),
        "event_id": event["id"],
        "summary": f"观察到信号：{event['signal']}",
        "raw_signal": event["signal"],
    }

    observations.append(observation)

    return observation

def find_observation(observation_id: str):
    # 在 observations 里查找指定 id 的 observation。
    for item in observations:
        if item["id"] == observation_id:
            return item

    return None


def generate_task(observation_id: str):
    # 先找到 observation。
    observation = find_observation(observation_id)

    # 找不到就返回 None。
    if observation is None:
        return None

    task = {
        "id": str(uuid4()),
        "observation_id": observation["id"],
        "title": f"基于观察生成任务：{observation['raw_signal']}",
        "status": "todo",
    }

    tasks.append(task)

    return task