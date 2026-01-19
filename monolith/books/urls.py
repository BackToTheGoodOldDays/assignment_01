from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookCatalogView.as_view(), name='catalog'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('api/list/', views.book_list_api, name='api_list'),
]
