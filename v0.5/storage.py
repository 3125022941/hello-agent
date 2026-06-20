# storage.py

# 这里先不用 MySQL，直接用 Python 列表当临时数据库。
# 注意：这些数据只存在内存里。
# 只要服务重启，列表里的数据就会全部清空。

events = []        # 保存事件 event
observations = []  # 保存观察 observation
tasks = []         # 保存任务 task