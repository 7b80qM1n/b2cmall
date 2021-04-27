from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('', views.AreasViewSet, '')

urlpatterns = [
    path('', include(router.urls)),
]