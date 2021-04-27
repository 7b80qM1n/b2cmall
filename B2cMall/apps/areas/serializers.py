from rest_framework import serializers
from . import models


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Area
        fields = ['id', 'name']

class SubsAreaSerializer(serializers.ModelSerializer):

    subs = AreaSerializer(many=True)

    class Meta:
        model = models.Area
        fields = ['id', 'name', 'subs']