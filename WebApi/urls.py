from django.urls import re_path, path

from WebApi import views, autoci

urlpatterns = [
    path('autoci', autoci.dispatcher, name='CI自动请求'),

    re_path(r'logs/(?P<session>\w+)-(?P<testcase>\w+)', autoci.GetLog, name='查看指定日志'),

    re_path(r'process/(?P<testname>\w+)', autoci.CheckProcess, name='检查任务进度'),

    path('query', views.getTestData, name='collection'),

    path('testmodule', views.getTestModules, name='test'),

    path('devices', views.getDevices, name='device'),

    path('insert', views.insertData, name='insert'),

    path('update', views.updateData, name='update'),

    path('start', views.startTest, name='startProject'),

    path('session/', views.log, name='home'),

    path('upload', views.uploadFile, name='upload'),
]