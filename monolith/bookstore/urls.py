"""
URL configuration for bookstore project.
Online Bookstore Management System - Monolithic Architecture
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Redirect root to books
    path('', RedirectView.as_view(url='/books/', permanent=False)),
    
    # Book routes - catalog, search, categories, authors
    path('books/', include('store.urls.book_urls')),
    
    # Cart and Order routes - shopping cart, checkout, orders
    path('cart/', include('store.urls.order_urls')),
    
    # Authentication routes - login, register, profile
    path('auth/', include('store.urls.customer_urls')),
    
    # Staff routes - inventory management, dashboard
    path('staff/', include('store.urls.staff_urls')),
]
