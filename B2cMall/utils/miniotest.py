import os
from minio import Minio
from minio.error import ResponseError
from django.core.files.storage import Storage
from utils.logger import log
from django.conf import settings
from django.utils.deconstruct import deconstructible

@deconstructible
class MinIOStorage(Storage):

    def __init__(self, bucket_name=None, endpoint=None, access_key=None, secret_key=None, secure=None):
        self.endpoint = endpoint or settings.ENDPOINT
        self.access_key = access_key or settings.ACCESS_KEY
        self.secret_key = secret_key or settings.SECRET_KEY
        self.secure = secure or settings.SECURE
        self.bucket_name = bucket_name or settings.BUCKET_NAME

    def _open(self, name, mode):
        pass

    def _save(self, name, content):
        """
        文件存储时调用此方法
        :param name: 要上传的文件名
        :param content: 以rb模式打开的文件对象
        :return:
        """
        print(self.access_key, self.secret_key, self.endpoint, self.secure)
        minioClient = Minio(endpoint=self.endpoint,
                            access_key=self.access_key,
                            secret_key='624904571@qq.com',
                            secure=self.secure)
        print(self.access_key,self.secret_key,self.endpoint,self.secure)
        try:
            # file_stat = os.stat('qq20210422103418.png')
            minioClient.put_object(settings.BUCKET_NAME, 'QQ截图20210422103418', content, 919816, content_type="image/jpeg")
        except ResponseError as err:
            log.error(err)
        else:
            return name

    def exists(self, name):
        """
        当要进行上传时都要调用此方法判断文件是否已上传,如果没有上传才会调用save方法进行上传
        :param name:要上传的文件名
        :return:True(表示文件已存在,不需要上传) False(文件不存在,需要上传)
        """
        return False

    def url(self, name):
        """
        当要访问图片时,就会调用此方法获取图片文件的绝对路径
        :param name:obj_name
        :return:
        """

        return f"http://{self.endpoint}{self.bucket_name}/{name}"
