from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(verbose_name='电话号码', max_length=11)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
