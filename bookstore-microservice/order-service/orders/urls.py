from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list),
    path('orders/<int:order_id>/', views.order_detail),
    path('orders/by-number/<str:order_number>/', views.order_by_number),
    path('orders/<int:order_id>/cancel/', views.cancel_order),
]
