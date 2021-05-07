from rest_framework import serializers
from goods import models


# 购物车新增修改序列化器
class CartSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品id', min_value=1)
    count = serializers.IntegerField(label='购买数量')
    selected = serializers.BooleanField(label='商品购买状态', default=True)

    def validate_sku_id(self, value):
        try:
            models.SKU.objects.get(id=value)
        except models.SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')

        return value


# 购物车查询序列化器
class SKUCartSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='购买数据')
    selected = serializers.BooleanField(label='商品购买状态')

    class Meta:
        model = models.SKU
        fields = ['id', 'name', 'default_image_url', 'price', 'count', 'selected']


# 购物车删除序列化器
class CartDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品id', min_value=1)

    def validate_sku_id(self, value):
        try:
            models.SKU.objects.get(id=value)
        except models.SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id不存在')

        return value
