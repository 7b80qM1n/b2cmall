
# redis配置
REDIS_PASS = 'jqmkfc039988'
SET_PATH = '127.0.0.1'
PORT = '8000'  # 服务器端口

# 手机验证码缓存的key值
PHONE_CACHE_KEY = 'sms_cache_'
# 验证码标记的key值
SEND_FLAG = 'send_flag'

# QQ互联
QQ_CLIENT_ID = None  # APPID
QQ_CLIENT_SECRET = None  # APPKEY
QQ_REDIRECT_URI = None  # 回调域名

# 邮箱
EMAIL_HOST = 'smtp.qq.com'  # 发送方的smtp服务器地址
EMAIL_PORT = 587  # smtp服务端口
EMAIL_HOST_USER = '624904571@qq.com'  # 发送方 邮箱地址
EMAIL_HOST_PASSWORD = 'nrjsstcebjqdbege'  # 获得的  授权码
EMAIL_USE_TLS = True  # 必须为True
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None
DEFAULT_FROM_EMAIL = '624904571@qq.com'  # 和 EMAIL_HOST_USER  相同

