from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('', views.QqoAuthUrlView, 'send_qq')

urlpatterns = [
    path('', include(router.urls)),
]