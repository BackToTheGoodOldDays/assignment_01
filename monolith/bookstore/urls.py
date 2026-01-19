"""
URL configuration for bookstore project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/books/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls')),
    path('cart/', include('cart.urls')),
]
