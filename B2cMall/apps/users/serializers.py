import re
from rest_framework import serializers
from . import models
from django_redis import get_redis_connection
from B2cMall.settings import const
from celery_task.email.tasks import send_verify_email
from users.utils import generate_email_verify_url

class UserRegisterModelSerializer(serializers.ModelSerializer):
    code = serializers.CharField(label='验证码', max_length=4, min_length=4, write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(read_only=True)  # 临时

    class Meta:
        model = models.User
        fields = ['mobile', 'password', 'code', 'username', 'allow', 'token']
        extra_kwargs = {
            'username': {'min_length': 5, 'max_length': 20, 'read_only': True,
                         'error_messages': {'min_length': '仅允许5-20个字符的用户名', 'max_length': '仅允许5-20个字符的用户名'}},
            'password': {'min_length': 8, 'max_length': 20, 'write_only': True,
                         'error_messages': {'min_length': '仅允许8-20个字符的密码', 'max_length': '仅允许8-20个字符的密码'}}
        }

    def _get_token(self, user):
        from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return token

    def validate(self, attrs):
        # 手机校验
        mobile = attrs.get('mobile')
        if not re.match("^1[3-9][0-9]{9}$", mobile):
            raise serializers.ValidationError('手机号格式错误')
        user = models.User.objects.filter(mobile=mobile).first()
        if user:
            raise serializers.ValidationError('该手机号码已注册,请直接登录')
        attrs['username'] = mobile  # 设置用户名

        # 协议校验
        allow = attrs.get('allow')
        if allow != 'true':
            raise serializers.ValidationError('请同意协议')

        # 校验验证码
        conn = get_redis_connection('verify_codes')
        sms_code = conn.get(f'{const.PHONE_CACHE_KEY}{mobile}')
        if sms_code is None:
            raise serializers.ValidationError('验证码失效,请重新发送')
        if attrs['code'] != sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):
        validated_data.pop('code')
        validated_data.pop('allow')
        # 添加用户
        user = models.User.objects.create_user(**validated_data)
        # # JWT 生成token
        token = self._get_token(user)
        user.token = token

        return user


class UserLoginModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = models.User
        fields = ['username', 'password', 'id']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    # 获取用户
    def _get_user(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        import re
        # 手机校验
        if re.match("^1[3-9][0-9]{9}$", username):
            user = models.User.objects.filter(mobile=username).first()
        # 邮箱校验
        # elif re.match("^.+@.+$", username):
        #     user = models.User.objects.filter(email=username).first()
        else:
            user = models.User.objects.filter(username=username).first()
        if user:
            ret = user.check_password(password)
            if ret:
                return user
            else:
                raise serializers.ValidationError('密码错误')
        else:
            raise serializers.ValidationError('用户不存在')

    # 获取token
    def _get_token(self, user):
        from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return token

    def validate(self, attrs):
        user = self._get_user(attrs)
        token = self._get_token(user)
        self.context['user'] = user
        self.context['token'] = token

        return attrs


class UserCenterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['username', 'mobile', 'id', 'email_action', 'email']


class UserMailViewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {'required': True},
        }

    def update(self, instance, validated_data):
        """在这里发激活邮件"""
        instance.email = validated_data.get('email')
        instance.save()
        verify_url = generate_email_verify_url(instance)
        send_verify_email.delay(instance.email, verify_url=verify_url)

        return instance


class UserAddressViewModelSerializer(serializers.ModelSerializer):
    # province = serializers.StringRelatedField(read_only=True)
    # city = serializers.StringRelatedField(read_only=True)
    # district = serializers.StringRelatedField(read_only=True)
    # province_id = serializers.IntegerField(label='省ID', required=True)
    # city_id = serializers.IntegerField(label='市ID', required=True)
    # district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = models.Address
        exclude = ('created_time', 'updated_time', 'is_delete', 'is_show')
        extra_kwargs = {
            'province': {'write_only': True},
            'city': {'write_only': True},
            'district': {'write_only': True},
        }

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

class UpdateTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ['title']