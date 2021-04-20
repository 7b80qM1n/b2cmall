from celery import Celery

# 创建实例对象
app = Celery('B2cMall')

# 加载配置文件
app.config_from_object('celery_task.config')

# 自动注册异步任务
app.autodiscover_tasks(['celery_task.sms'])