from django.db import models
from utils.models import BaseModel
from users.models import User

class OauthQQUser(BaseModel):
    user = models.ForeignKey(to=User, on_delete=True, verbose_name='用户')
    openid = models.CharField(max_length=64, db_index=True, verbose_name='openid')

    class Meta:
        db_table = "tb_oauth_qq"
        verbose_name = "用户数据"
        verbose_name_plural = verbose_name
