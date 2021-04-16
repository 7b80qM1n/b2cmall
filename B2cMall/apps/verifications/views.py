from rest_framework.views import APIView
from libs.tencent_sms import sms
from django_redis import get_redis_connection
from B2cMall.settings import const
from utils.response import APIResponse
from utils.logger import log
from rest_framework import status

class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        # 创建redis连接对象
        conn = get_redis_connection('verify_codes')
        # 获取标记
        send_flag = conn.get(const.SEND_FLAG)
        if send_flag:
            return APIResponse(code=0, msg='短信发送频繁', status=status.HTTP_400_BAD_REQUEST)
        # 生成验证码
        code = sms.get_code()
        # 发送短信
        # result = sms.send_sms(mobile, code)
        # 短信测试
        result = True

        log.warning(code)

        # 验证码保存
        conn.setex(f'{const.PHONE_CACHE_KEY}{mobile}', 60, code)
        # 保存标记,表示此手机号已发送过短信,有效期60s
        conn.setex(f'{const.SEND_FLAG}', 60, code)

        if result:
            return APIResponse(code=1, msg='验证码发送成功')
        else:
            return APIResponse(code=0, msg='验证码发送失败,请稍候重试')