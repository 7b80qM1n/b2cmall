from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet
from utils.response import APIResponse
from . import models, serializers

class RegisterView(GenericViewSet, CreateModelMixin):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserRegisterModelSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        username = response.data.get('username')
        token = response.data.get('token')
        return APIResponse(code=1, msg='注册成功', username=username, token=token)


class LoginView(ViewSet):

    # 验证手机是否存在
    @action(methods=['GET'], detail=False)
    def check_telephone(self, request, *args, **kwargs):
        mobile = request.query_params.get('mobile')
        import re
        if not re.match('^1[3-9][0-9]{9}$', mobile):
            return APIResponse(code=0, msg='手机号不合法')

        try:
            models.User.objects.get(mobile=mobile)
            return APIResponse(code=1, msg='手机号存在')
        except:
            return APIResponse(code=0, msg='手机号不存在')

    # 用户名/手机号+密码登陆
    @action(methods=['POST'], detail=False)
    def login(self, request, *args, **kwargs):
        ser = serializers.UserLoginModelSerializer(data=request.data)
        if ser.is_valid():
            token = ser.context['token']
            username = ser.context['user'].username
            user_id = ser.context['user'].id
            return APIResponse(code=1, msg='登陆成功', token=token, username=username, user_id=user_id)
        else:
            return APIResponse(code=0, msg=ser.errors)
