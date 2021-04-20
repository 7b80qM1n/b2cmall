from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings


def generate_save_user_token(openid):
    # (密钥, 有效时间)
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)
    # 字典数据,返回bytes类型
    openid = serializer.dumps({"openid": openid}).decode()
    return openid

def check_save_user_token(openid_token):
    # 校验
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=600)
    try:
        # 校验失败会抛出itsdangerous.BadData异常
        data = serializer.loads(openid_token)
    except BadData:
        return None
    else:
        return data.get('openid')