from django.urls import path
from . import views

urlpatterns = [
    path('customers/register/', views.register),
    path('customers/login/', views.login),
    path('customers/profile/', views.profile),
    path('customers/', views.list_customers),
    path('customers/<int:customer_id>/', views.get_customer_by_id),
    path('customers/addresses/', views.addresses),
    path('customers/addresses/<int:address_id>/', views.address_detail),
]
