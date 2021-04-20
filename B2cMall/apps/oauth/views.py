from QQLoginTool.QQtool import OAuthQQ
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from utils.response import APIResponse
from utils.logger import log
from . import models
from . import utils
from . import serializers

class QqoAuthUrlView(ViewSet):
    """
    QQ登录接入
    1.后端写好生成QQ登录界面地址接口,前端发请求获取QQ登录界面地址
    2.前端跳转到链接地址让用户登录,成功后QQ服务器会把code拼接到回调地址返回给前端,前端拿到code后再次向后端发请求,把code传递给后端
    3.后端拿到code后,通过code向QQ服务器获取access_token,获取后通过access_token向QQ服务器再获取openid
    """

    # 生成QQ登录网址
    @action(methods=['GET'], detail=False)
    def login_url(self, request, *args, **kwargs):
        # 1.提取前端传入的next参数记录用户从哪里来到登录界面
        next_index = request.query_params.get('next') or '/'

        # 2.创建QQ登录对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next_index)
        # 3.调用get_qq_url方法,获取到拼接好的QQ登录网址
        login_url = oauth.get_qq_url()
        return APIResponse(code=1, msg='请求成功', login_url=login_url)

    # QQ登录
    @action(methods=['GET'], detail=False)
    def g_openid(self, request, *args, **kwargs):
        # 1.获取前端传入的code
        code = request.query_params.get('code')
        if not code:
            return APIResponse(code=0, msg='缺少code')

        # 2.创建QQ登录对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 3.调用get_access_token方法,用code获取到Access Token
            access_token = oauth.get_access_token(code)
            # 4.调用get_access_token方法,用Access Token获取到OpenID
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            log.info(e)
            return APIResponse(code=0, msg='QQ服务器不可用', status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # 5.查询数据库有没有这个openid
            qq_user_obj = models.OauthQQUser.objects.get(openid=openid)
        except models.OauthQQUser.DoesNotExist as e:
            # 没有openid,表示新用户,返回加密后的openid,前端暂存,获取信息后再绑定
            openid_token = utils.generate_save_user_token(openid)
            return APIResponse(code=0, msg='新用户', openid_token=openid_token)
        else:
            # 有openid,返回JWT
            user = qq_user_obj.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return APIResponse(code=1, msg='成功', username=user.username, token=token)

# 新用户绑定信息
class QqoAuthInfoView(GenericViewSet, CreateModelMixin):
    queryset = models.User.objects.all()
    serializer_class = serializers.QqoAuthInfoSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        username = response.data.get('username')
        token = response.data.get('token')
        return APIResponse(code=1, msg='绑定成功', username=username, token=token)
