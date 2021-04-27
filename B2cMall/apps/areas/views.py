from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from . import models, serializers

class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):

    def get_queryset(self):
        if self.action == 'list':
            return models.Area.objects.filter(parent=None)
        else:
            return models.Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubsAreaSerializer
