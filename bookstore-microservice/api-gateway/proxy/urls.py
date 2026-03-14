from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^(?P<service_name>[^/]+)/(?P<path>.*)$', views.proxy_request),
]
