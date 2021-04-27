from django.urls import path, include, re_path
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('register', views.RegisterView, 'register')
router.register('', views.LoginView, 'login')
router.register('', views.EmailVerifyView, '')
router.register('address', views.UserAddressView, '')

urlpatterns = [
    path('', include(router.urls)),
    re_path('info/$', views.UserDetailView.as_view()),
    re_path('email/$', views.UserMailView.as_view()),
]