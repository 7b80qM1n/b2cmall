import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from minio import Minio, ResponseError
from minio.error import NoSuchBucketPolicy
import json
import uuid
import random
import string


@deconstructible
class MinioStorage(Storage):
    """
    python docs:  https://docs.min.io/docs/python-client-api-reference.html
    @:param fp : fileobject
    @:param object_name is the object name which will save to  minio bucket
    @:param bucket_name the bucket name of minio .
    """

    def __init__(self, bucket_name=None, object_name=None):
        if not settings.MINIO_CONF:
            raise ValueError('required MINIO_CONF  config in django.settings: format is:\n{}'.format(
                {'endpoint': '192.168.110.151:9000',
                 'access_key': 'username',
                 'secret_key': 'password',
                 'secure': False,
                 }
            ))
        self.minio_conf = settings.MINIO_CONF
        if not settings.BUCKET_NAME:
            self.bucket_name = bucket_name
        self.bucket_name = settings.BUCKET_NAME
        self.object_name = object_name
        self.endpoint_minio = settings.MINIO_CONF.get('endpoint', None)
        self.minio_client = Minio(**self.minio_conf)

    def _open(self, name, mode='rb'):
        """ for read file : Retrieve the specified file from storage."""
        return super().open(name, 'rb')

    def _save(self, name, content, max_length=None):
        filename, extendname = name.split('.')
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 7))
        name = name.replace(filename, uuid.uuid1().hex + salt + '_' + filename)
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)
        try:
            self.minio_client.get_bucket_policy(self.bucket_name)
        except NoSuchBucketPolicy:
            self.set_bucket_policy_public(self.bucket_name)
        (etag, vid) = self.minio_client.put_object(bucket_name=self.bucket_name, object_name=name, data=content,
                                                   length=content.size)
        if etag:
            # print("save return  minio is {}".format('/{}/{}'.format(self.bucket_name,name)))
            # 这里返回name,就是url方法的入参name
            name_file = '{}/{}'.format(self.bucket_name, name)
            return name_file

    def url(self, name):
        print("url minio return is {}".format(self.endpoint_minio + '/{}/{}'.format(self.bucket_name, name)))
        return self.endpoint_minio + '/' + name

    def exists(self, name):
        """ means filename always is available is new filename, fast-dfs always  storage one same file """
        return False

    def set_bucket_policy_public(self, bucket_name):
        """set file to public download by url: http:endpoint/bucket_name/object-name"""

        policy = {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow',
                                                          'Principal': {'AWS': ['*']},
                                                          'Action': ['s3:GetBucketLocation', 's3:ListBucket'],
                                                          'Resource': ['arn:aws:s3:::{}'.format(bucket_name)]},
                                                         {'Effect': 'Allow', 'Principal': {'AWS': ['*']},
                                                          'Action': ['s3:GetObject'],
                                                          'Resource': ['arn:aws:s3:::{}/*'.format(bucket_name)]}]}
        # set  bucket to public download
        self.minio_client.set_bucket_policy(bucket_name=bucket_name, policy_access=json.dumps(policy))

    def get_minio_object(self, bucket_name, object_name):
        """ :return minio object of file,if get bytes by read()"""
        response = None
        try:
            response = self.minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
        finally:
            response.close()
            response.release_conn()