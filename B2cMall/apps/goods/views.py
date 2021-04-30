from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import ViewSetMixin
from .paginations import PageNumberPagination
from . import models, serializers

class SKUListView(ViewSetMixin, ListAPIView):
    """
    获取商品列表
    """
    queryset = models.SKU.objects.filter(is_launched=True)
    serializer_class = serializers.SKUListSerializers

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ('category',)
    ordering_fields = ('create_time', 'price', 'sales')
    pagination_class = PageNumberPagination
