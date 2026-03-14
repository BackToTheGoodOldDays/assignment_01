from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('statuses', views.BookStatusViewSet)
router.register('books', views.BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
