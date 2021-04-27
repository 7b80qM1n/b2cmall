from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('sku', views.SKUListView, '')

urlpatterns = [
    path('', include(router.urls)),
]