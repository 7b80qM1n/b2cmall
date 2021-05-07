import pickle
import base64
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.response import APIResponse
from . import serializers
from rest_framework import status
from goods import models

class CartView(APIView):
    """
    购物车登录未登录增删改查
    """
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request):
        """新增"""
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        user = request.user
        # 登录用户 存redis
        if user.is_authenticated:
            """
            hash
            cart_user.id:{1:2, 16:1} 商品id和商品数量
            set
            selected_user.id:{1, } 是否勾选,勾选的就存,存商品id
            """
            # 创建redis连接对象
            conn = get_redis_connection('cart')
            pl = conn.pipeline()
            # 如果添加到sku_id在hash中已经存在,需要做增量
            pl.hincrby(f'cart_{user.id}', sku_id, count)
            # 把勾选的商品sku_id 存储到set集合中
            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            pl.execute()

            return APIResponse(result=serializer.data)

        # 未登录用户 存cookie
        else:
            """
            cart:{
                1:{'count':1,'selected':True},
                16:{'count':1,'selected':False},
                }
            """
            # 获取cookie购物车数据
            cart_str = request.COOKIES.get('cart')
            # 购物车有商品,拿出字典,无创建
            if cart_str:
                #  把字符串转换成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 把bytes类型的字符串转换成bytes类型
                cart_bytes = base64.b64decode(cart_str_bytes)
                # 把bytes类型转换成字典
                cart_dict = pickle.loads(cart_bytes)
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                # 存在修改数量
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            # 把新的商品添加到cart_dict中
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 先将字典转换成bytes
            cart_bytes = pickle.dumps(cart_dict)
            # 再讲bytes类型转换成bytes类型的字符串
            cart_str_bytes = base64.b64encode(cart_bytes)
            # 把bytes类型的字符串转换成字符串
            cart_str = cart_str_bytes.decode()

            # 设置cookie
            APIResponse(result=serializer.data).set_cookie('cart', cart_str)

            return APIResponse(result=serializer.data)

    def get(self, request):
        user = request.user
        # 获取登录用户redis购物车数据
        if user.is_authenticated:
            """
            hash
            cart_user.id:{1:2, 16:1} 商品id和商品数量
            set
            selected_user.id:{1, } 是否勾选,勾选的就存,存商品id
            """
            # 创建redis连接对象
            conn = get_redis_connection('cart')
            # 获取hash {商品id和商品数量, 商品id和商品数量}
            cart_redis_dict = conn.hgetall(f'cart_{user.id}')
            # 获取set  {商品id, 商品id, }
            selecteds = conn.smembers(f'selected_{user.id}')
            # 转换数据类型,和下面cookie一致,为了方便之后序列化
            # cart_dict = {1:{'count':1,'selected':True}, 16:{'count':1,'selected':False}, }
            cart_dict = {}
            if cart_redis_dict:
                for sku_id_bytes, count_bytes in cart_redis_dict.items():
                    cart_dict[int(sku_id_bytes)] = {
                        'count': int(count_bytes),
                        'selected': sku_id_bytes in selecteds,
                    }
            else:
                return APIResponse(code=0, msg='没有购物车数据', status=status.HTTP_400_BAD_REQUEST)

        # 获取未登录用户cookie数据
        else:
            """
            cart:{
                1:{'count':1,'selected':True},
                16:{'count':1,'selected':False},
                }
            """
            # 获取cookie购物车数据
            cart_str = request.COOKIES.get('cart')
            # 存在,获取数据并转换回字典
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            # 不存在,直接返回
            else:
                return APIResponse(code=0, msg='没有购物车数据', status=status.HTTP_400_BAD_REQUEST)

        # 根据sku_id 查询sku模型
        sku_ids = cart_dict.keys()

        # 给模型对象添加count和selected属性
        skus = models.SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']
        # 创建序列化器进行序列化

        serializer = serializers.SKUCartSerializer(skus, many=True)

        return APIResponse(result=serializer.data)

    def put(self, request):
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        user = request.user

        # 修改登录用户redis购物车数据
        if user.is_authenticated:
            # 创建redis连接对象
            conn = get_redis_connection('cart')
            # 创建管道
            pl = conn.pipeline()
            # 设置hash {商品id和商品数量, 商品id和商品数量}
            pl.hset(f'cart_{user.id}', sku_id, count)
            # 如果勾选就把勾选商品的sku_id存储到set集合
            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            else:
                pl.srem(f'selected_{user.id}', sku_id)

            pl.execute()

            return APIResponse(result=serializer.data)
        # 修改未登录用户cookie数据
        else:
            cart_str = request.COOKIES.get('cart')
            # 存在,获取需要修改的数据并转换成字典
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            # 不存在,直接返回
            else:
                return APIResponse(code=0, msg='没有购物车数据', status=status.HTTP_400_BAD_REQUEST)
            # 覆盖原有的数据
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将字典转回字符串
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 设置cookie
            APIResponse(result=serializer.data).set_cookie('cart', cart_str)

            return APIResponse(result=serializer.data)

    def delete(self, request):
        serializer = serializers.CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')

        user = request.user

        # 删除登录用户redis购物车数据
        if user.is_authenticated:
            # 创建redis连接对象
            conn = get_redis_connection('cart')
            # 创建管道
            pl = conn.pipeline()
            # 删除hash {商品id和商品数量, 商品id}
            pl.srem(f'cart_{user.id}', sku_id)

            pl.execute()

            return APIResponse(status=status.HTTP_204_NO_CONTENT)
        # 删除未登录用户cookie数据
        else:
            cart_str = request.COOKIES.get('cart')
            # 存在,获取需要删除的数据并转换成字典
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            # 不存在,直接返回
            else:
                return APIResponse(code=0, msg='没有购物车数据', status=status.HTTP_400_BAD_REQUEST)
            # 根据sku_id删除数据
            if sku_id in cart_dict:
                del cart_dict[sku_id]

            #  cookie还有值就设置返回
            if len(cart_dict.keys()):
                # 将字典转回字符串
                cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                APIResponse(result=serializer.data).set_cookie('cart', cart_str)
                return APIResponse(status=status.HTTP_204_NO_CONTENT)
            else:
                # 没有值了就清空cookie
                APIResponse(result=serializer.data).delete_cookie('cart')
                return APIResponse(status=status.HTTP_204_NO_CONTENT)

