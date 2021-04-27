from celery import Celery

# 创建实例对象
app = Celery('B2cMall')

# 加载配置文件
app.config_from_object('celery_task.config')

# 自动注册异步任务
# app.autodiscover_tasks(['celery_task.sms', 'celery_task.email', 'celery_task.html'])
app.autodiscover_tasks(['celery_task.test_time', 'celery_task.html'])

# 时区
app.conf.timezone = 'Asia/Shanghai'
# 是否使用UTC
app.conf.enable_utc = False

# 任务的定时配置
from datetime import timedelta

app.conf.beat_schedule = {
    'get_index_static': {
        'task': 'celery_task.test_time.tasks.get_index_static',  # 路径
        'schedule': timedelta(minutes=1),
    }
}