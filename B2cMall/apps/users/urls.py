from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('register', views.RegisterView, 'register')
router.register('', views.LoginView, 'login')

urlpatterns = [
    path('', include(router.urls)),
]