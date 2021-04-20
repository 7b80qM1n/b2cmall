import re

from django_redis import get_redis_connection
from rest_framework import serializers

from settings import const
from . import models
from . import utils


class QqoAuthInfoSerializer(serializers.ModelSerializer):
    openid_token = serializers.CharField(label='操作凭证')
    code = serializers.CharField(label='验证码', max_length=4, min_length=4, write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = models.User
        fields = ['mobile', 'password', 'code', 'openid_token', 'token']
        extra_kwargs = {
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
        # 验证码校验
        conn = get_redis_connection('verify_codes')
        sms_code = conn.get(f'{const.PHONE_CACHE_KEY}{mobile}')
        if sms_code is None:
            raise serializers.ValidationError('验证码失效,请重新发送')
        if attrs['code'] != sms_code.decode():
            raise serializers.ValidationError('验证码错误')
        # openid校验
        openid_token = attrs.pop('openid_token')
        openid = utils.check_save_user_token(openid_token)
        if not openid:
            raise serializers.ValidationError('openid已失效')
        attrs['openid'] = openid
        # 拿手机号查询 user表, 如果能查到说明手机号已注册,校验密码是否和用户匹配
        try:
            user = models.User.objects.get(mobile=mobile)
        except mobile.User.DoesNotExist:
            pass
        else:
            # 校验密码是否和用户匹配
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            else:
                attrs['user'] = user
        return attrs

    def create(self, validated_data):
        """
        1.获取validated_data中的user,能取到说明用户存在,直接绑定openid
        2.如果没有取到,则要添加新用户,再绑定openid
        3.返回user
        """
        validated_data.pop('code')

        user = validated_data.get('user')
        if not user:
            # 添加新用户
            validated_data['username'] = validated_data.get('mobile')
            user = models.User.objects.create_user(**validated_data)
        # 绑定openid
        models.OauthQQUser.objects.create(user=user, openid=validated_data.get('openid'))
        # JWT 生成token
        token = self._get_token(user)
        user.token = token
        return user
