from rest_framework import serializers
from . import models


class SKUListSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.SKU
        fields = ['id', 'name', 'default_image_url', 'comments']
