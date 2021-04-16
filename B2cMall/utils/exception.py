from rest_framework.views import exception_handler
from django.db import DatabaseError
from redis.exceptions import ReadOnlyError
from B2cMall.utils.response import APIResponse
from utils.logger import log

def common_exception_handler(exc, context):
    """
    自定义异常处理
    :param exc: 异常实例对象
    :param context: 抛出异常的上下文(包含request和view对象)
    :return:
    """
    log.error(f'视图{context["view"].__class__.__name__}出错,错误:{str(exc)}')
    ret = exception_handler(exc, context)
    if not ret:
        if isinstance(exc, KeyError):
            return APIResponse(code=0, msg='key error')
        elif isinstance(exc, DatabaseError) or isinstance(exc, ReadOnlyError):
            return APIResponse(code=0, msg='服务器内部错误')
        return APIResponse(code=0, msg='error', result=str(exc))
    else:
        return APIResponse(code=0, msg='error', result=ret.data)