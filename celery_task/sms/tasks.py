from celery_task.sms.tencent_sms.sms import send_sms
from celery_task.celery import app

@app.task(name="send_sms")  # 注册任务
def send_sms_code(mobile, code):
    ret = send_sms(mobile, code)
    return ret