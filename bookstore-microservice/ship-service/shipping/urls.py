from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('shipping-methods', views.ShippingMethodViewSet)
router.register('shipments', views.ShipmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
