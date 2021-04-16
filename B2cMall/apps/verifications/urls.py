from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path('smscode/(?P<mobile>1[3-9][0-9]{9})/$', views.SMSCodeView.as_view()),
]
