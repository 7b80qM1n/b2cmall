from B2cMall.settings import const

broker_url = f'redis://:{const.REDIS_PASS}@{const.SET_PATH}:6379/7'  # 任务队列
backend_url = f'redis://:{const.REDIS_PASS}@{const.SET_PATH}:6379/8'  # 结构存储

