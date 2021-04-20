from celery_task.celery import app

@app.task()
def add():
    return '121212'