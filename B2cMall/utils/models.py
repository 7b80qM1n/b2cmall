from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    class Meta:
        abstract = True  # 抽象模型类 仅继承 不创建表
