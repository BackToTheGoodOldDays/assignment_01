from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('authors', views.AuthorViewSet)
router.register('publishers', views.PublisherViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
