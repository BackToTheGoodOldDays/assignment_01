"""Customer/Auth URL configuration."""
from django.urls import path
from store.controllers.customerController.customer_controller import (
    RegisterView, login_view, logout_view, profile_view,
)

app_name = 'customer'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]
