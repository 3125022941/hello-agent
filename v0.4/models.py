# models.py
#
# 这个文件负责定义“数据库表模型”。
#
# 在 v0.2 里，models.py 只是 Pydantic 的返回模型：
# 它只告诉 FastAPI：接口返回的数据长什么样。
#
# 到 v0.3 以后，我们开始接 SQLite。
# 所以这里改用 SQLModel，并且给类加上 table=True。
#
# table=True 的意思是：
# 这个类不仅是一个 Python 数据模型，
# 还会对应 SQLite 数据库里的一张真实数据表。
#
# 简单记：
#
# Event       -> events 相关数据
# Observation -> observations 相关数据
# Task        -> tasks 相关数据
#
# 现在先不做复杂外键关系。
# 先用 event_id / observation_id 这样的字符串字段保存关联关系。
# 等你理解 SQLite 和 SQLModel 基础之后，再升级成正式 ForeignKey。

from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    # Event 表示“事件”。
    #
    # 一条 event 是系统观察到的原始信号。
    #
    # 例子：
    # 用户最近反复提到 AI Agent
    # 用户在 GitHub 看到一个有价值的项目
    # 用户从小红书/闲鱼/群聊里捕捉到一个机会
    #
    # SQLModel, table=True 表示：
    # 这个类会被 SQLModel 映射成数据库表。

    # id 是事件的唯一标识。
    #
    # primary_key=True 表示它是数据库表的主键。
    # 主键的作用是唯一定位一条记录。
    #
    # 这里用 str，是因为我们后面会用 uuid4() 生成字符串 id。
    id: str = Field(primary_key=True)

    # signal 是原始信号内容。
    #
    # 这是 event 最核心的字段。
    # 用户创建事件时必须提供它。
    signal: str

    # source 表示信号来源。
    #
    # 例如：
    # obsidian
    # github
    # chat
    # browser
    #
    # Optional[str] = None 表示这个字段可以不填。
    source: Optional[str] = None

    # note 表示补充备注。
    #
    # 用来记录一些额外上下文。
    # 例如：“这个话题今天出现了三次”。
    #
    # 它也是可选字段。
    note: Optional[str] = None


class Observation(SQLModel, table=True):
    # Observation 表示“观察”。
    #
    # 一条 observation 是系统基于 event 提取出来的理解。
    #
    # event 更像原始材料：
    # “用户最近频繁关注 AI Agent”
    #
    # observation 更像初步判断：
    # “观察到一个关于 AI Agent 学习/项目方向的信号”

    # observation 自己的唯一 id。
    id: str = Field(primary_key=True)

    # 这里先用字符串保存 event_id。
    # 后面学外键时，再正式加 ForeignKey。
    #
    # event_id 用来说明：
    # 这条 observation 是从哪一条 event 生成的。
    #
    # 例如：
    # event.id = "abc"
    # observation.event_id = "abc"
    #
    # 这样以后就能从 observation 追溯回原始 event。
    event_id: str

    # summary 是对原始信号的总结。
    #
    # 现在 v0.3 先用简单规则生成。
    # 后面接 LLM 后，可以让模型生成更聪明的 summary。
    summary: str

    # raw_signal 保存原始 signal。
    #
    # 虽然 event_id 已经能追溯回 event，
    # 但这里额外保存一份 raw_signal，可以让 observation 自己更完整。
    #
    # 对学习阶段来说，这样更直观。
    raw_signal: str


class Task(SQLModel, table=True):
    # Task 表示“任务”。
    #
    # 一条 task 是系统根据 observation 生成的行动项。
    #
    # 例子：
    # “整理 AI Agent 相关概念”
    # “写一个最小 FastAPI demo”
    # “阅读 LangGraph 入门文档”

    # task 自己的唯一 id。
    id: str = Field(primary_key=True)

    # observation_id 表示：
    # 这个任务是根据哪一条 observation 生成的。
    #
    # 现在先用字符串保存关联关系。
    # 后面可以升级成数据库外键。
    observation_id: str

    # title 是任务标题。
    #
    # 这是用户最容易看到的字段。
    # 它应该是一句可以直接执行的话。
    title: str

    # status 是任务状态。
    #
    # 当前先用字符串即可。
    # 比如：
    # todo    = 待完成
    # doing   = 进行中
    # done    = 已完成
    status: str

class Review(SQLModel,table=True):
    # Review 表示“复盘”。
    #
    # 一条 review 是用户完成或推进某个 task 后，
    # 对这个任务做的一次简单总结。
    #
    # 例如：
    # task: “阅读 SQLModel 官方教程”
    # review: “今天理解了 session 和 commit，卡在外键关系”
    
    id:str=Field(primary_key=True)

    task_id:str

    summary:str

    score:int

    created_at: datetime = Field(default_factory=datetime.utcnow)