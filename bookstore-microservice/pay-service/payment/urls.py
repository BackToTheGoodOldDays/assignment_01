from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('payment-methods', views.PaymentMethodViewSet)
router.register('payments', views.PaymentViewSet)

urlpatterns = [path('', include(router.urls))]
