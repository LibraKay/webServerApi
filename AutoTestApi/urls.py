from django.urls import path

from . import views, autotest

urlpatterns = [
    path('api', autotest.dispatcher, name='自动化测试接口'),
]