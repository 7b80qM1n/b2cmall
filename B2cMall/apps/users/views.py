from django_redis import get_redis_connection
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ViewSet, ViewSetMixin
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, CreateAPIView
from utils.response import APIResponse
from . import models, serializers
from .utils import check_email_verify_url
from goods.models import SKU

# 注册视图 post/ users/register/
class RegisterView(GenericViewSet, CreateModelMixin):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserRegisterModelSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        username = response.data.get('username')
        token = response.data.get('token')
        return APIResponse(code=1, msg='注册成功', username=username, token=token)


# 登录视图
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


# 用户中心详情视图 get/ users/info/
class UserDetailView(RetrieveAPIView):
    # queryset = models.User.objects.all()
    serializer_class = serializers.UserCenterModelSerializer
    permission_classes = [IsAuthenticated]

    # 重写要返回的模型对象
    def get_object(self):
        return self.request.user


# 用户中心修改and激活邮件视图 put/ users/email/
class UserMailView(UpdateAPIView):
    serializer_class = serializers.UserMailViewModelSerializer
    permission_classes = [IsAuthenticated]

    # 重写要返回的模型对象
    def get_object(self):
        return self.request.user


# 激活邮箱回调 get/  users/email/
class EmailVerifyView(ViewSet):

    @action(methods=['GET'], detail=False)
    def verifycation(self, request, *args, **kwargs):
        # 获取前端查询字符串传入的token
        token = request.query_params.get('token')
        # 解密token并查询对应的user
        user = check_email_verify_url(token)
        if not user:
            return APIResponse(code=0, msg='链接失效,请重新激活', status=status.HTTP_400_BAD_REQUEST)
        # 修改当前user的email_action为True
        user.email_action = True
        user.save()

        return APIResponse(code=1, msg='激活成功', username=user.username)

# 收货地址的增删查改  users/address
class UserAddressView(UpdateModelMixin, GenericViewSet):
    """收货地址的增删查改"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserAddressViewModelSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_show=True, is_delete=False)

    def create(self, request, *args, **kwargs):
        user = request.user
        count = user.addresses.filter(is_delete=False, is_show=True).count()
        if count >= 20:
            return APIResponse(code=0, msg='收货地址最多20个', status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse(code=1, msg='成功', result=serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = request.user
        return APIResponse(user_id=user.id, default_address_id=user.default_address_id, limit=20, addresses=serializer.data)

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        address.is_delete = True
        address.save()
        return APIResponse(code=1, msg='删除成功')

    @action(methods=['PUT'], detail=True)
    def title(self, request, pk=None):
        address = self.get_object()
        serializer = serializers.UpdateTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse(code=1, msg='标题修改成功')

    @action(methods=['PUT'], detail=True)
    def status(self, request, pk=None):
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return APIResponse(code=1, msg='默认地址设置成功')

# 用户商品浏览记录保存  post/get  users/browse_histories
class AddUserCookiesView(ViewSetMixin, CreateAPIView):

    serializer_class = serializers.AddUserCookiesSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(result=serializer.data, status=status.HTTP_201_CREATED)

    # 获取浏览记录
    def get(self, request):
        user = request.user
        conn = get_redis_connection('history_codes')
        history_list = conn.lrange(f'history_{user.id}', 0, -1)

        sku_obj_list = []
        for sku_id in history_list:
            sku_obj = SKU.objects.get(id=sku_id)
            sku_obj_list.append(sku_obj)

        serializer = serializers.SKUSerialize(sku_obj_list, many=True)

        return APIResponse(result=serializer.data)





