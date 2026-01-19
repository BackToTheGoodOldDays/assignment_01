"""
URL configuration for Clean Architecture bookstore project.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/books/', permanent=False)),
    
    # Account URLs
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile_view, name='profile'),
    
    # Book URLs
    path('books/', views.catalog_view, name='catalog'),
    path('books/<int:pk>/', views.book_detail_view, name='book_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:book_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:book_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart_view, name='clear_cart'),
    path('cart/api/', views.cart_api_view, name='cart_api'),
]
