# database.py
#
# 这个文件负责数据库连接。
#
# models.py 定义的是“表长什么样”。
# database.py 定义的是“怎么连接数据库、怎么创建表、怎么拿到 session”。
#
# 在 v0.3 里，我们先使用 SQLite。
# SQLite 的特点是：不需要单独启动数据库服务，只会生成一个 .db 文件。
#
# 也就是说，程序运行后，会在项目目录下生成：
#
# learning_observer.db

from sqlmodel import Session, SQLModel, create_engine

# SQLite 数据库文件名。
#
# 如果这个文件不存在，SQLite 会自动创建它。
# 如果这个文件已经存在，程序会继续使用里面的数据。
sqlite_file_name = "learning_observer.db"

# SQLite 的连接地址。
#
# sqlite:/// 表示使用本地 SQLite 文件。
# 后面的 learning_observer.db 就是数据库文件名。
sqlite_url = f"sqlite:///{sqlite_file_name}"

# FastAPI 可能会在不同线程里处理请求。
#
# SQLite 默认不允许同一个连接跨线程使用。
# check_same_thread=False 是 FastAPI + SQLite 常见配置。
connect_args = {"check_same_thread": False}

# engine 可以理解成“数据库引擎”或者“数据库连接器”。
#
# 后面所有数据库操作，都会通过这个 engine 连接到 SQLite。
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    # 根据 models.py 里所有 table=True 的 SQLModel 类创建数据库表。
    #
    # 例如：
    # Event       -> event 表
    # Observation -> observation 表
    # Task        -> task 表
    #
    # 如果表已经存在，不会重复创建。
    SQLModel.metadata.create_all(engine)


def get_session():
    # session 可以理解成“一次数据库操作窗口”。
    #
    # 你要查询、插入、修改、删除数据，都需要通过 session。
    #
    # yield session 是 FastAPI 依赖注入常用写法：
    # 接口开始时创建 session，
    # 接口结束后自动关闭 session。
    with Session(engine) as session:
        yield session