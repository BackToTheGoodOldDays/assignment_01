from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookStatusViewSet, BookTagViewSet, BookViewSet,
    BookImageViewSet, BookDescriptionViewSet,
    BookRatingViewSet, BookInventoryViewSet
)

router = DefaultRouter()
router.register(r'statuses', BookStatusViewSet, basename='bookstatus')
router.register(r'tags', BookTagViewSet, basename='booktag')
router.register(r'books', BookViewSet, basename='book')
router.register(r'images', BookImageViewSet, basename='bookimage')
router.register(r'descriptions', BookDescriptionViewSet, basename='bookdescription')
router.register(r'ratings', BookRatingViewSet, basename='bookrating')
router.register(r'inventory', BookInventoryViewSet, basename='bookinventory')

urlpatterns = [
    path('', include(router.urls)),
]
