from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'statuses', views.CartStatusViewSet, basename='cartstatus')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'items', views.CartItemViewSet, basename='cartitem')
router.register(r'saved', views.SavedCartViewSet, basename='savedcart')

urlpatterns = [
    path('', include(router.urls)),
    path('create-for-customer/', views.create_for_customer, name='create-for-customer'),
    path('active-cart/', views.get_active_cart, name='active-cart'),
]
