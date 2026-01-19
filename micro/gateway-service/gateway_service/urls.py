"""Gateway Service URL Configuration."""
from django.urls import path, include

urlpatterns = [
    path('', include('gateway.urls')),
]
