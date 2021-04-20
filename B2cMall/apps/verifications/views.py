import random
from celery_task.sms.tasks import send_sms_code
from rest_framework.views import APIView
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
        send_flag = conn.get(f'{const.SEND_FLAG}{mobile}')
        if send_flag:
            return APIResponse(code=0, msg='短信发送频繁', status=status.HTTP_400_BAD_REQUEST)

        # 生成验证码
        code = str(random.randrange(1000, 9999))
        log.warning(code)

        # 发送短信
        send_sms_code.delay(mobile, code)

        # 创建管道
        pl = conn.pipeline()
        # 验证码保存
        pl.setex(f'{const.PHONE_CACHE_KEY}{mobile}', 60, code)
        # 保存标记,表示此手机号已发送过短信,有效期60s
        pl.setex(f'{const.SEND_FLAG}{mobile}', 60, code)
        # 执行管道
        pl.execute()

        return APIResponse(code=1, msg='验证码发送成功')