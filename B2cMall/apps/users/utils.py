from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings
from . import models

def generate_email_verify_url(user):
    # (密钥, 有效时间)
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60*60*24)
    # 字典数据,返回bytes类型
    token = serializer.dumps({"user_id": user.id, "user_email": user.email}).decode()
    # 拼接链接
    return 'https://7b80qm1n.cn/index.html?token=' + token


def check_email_verify_url(token):
    """解密token并查询对应的user"""
    # 校验
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)
    try:
        # 校验失败会抛出itsdangerous.BadData异常
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('user_email')
        try:
            user = models.User.objects.get(id=user_id, email=email)
        except models.User.DoesNotExist:
            return None
        else:
            return user
