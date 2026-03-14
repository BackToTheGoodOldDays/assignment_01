from django.urls import path
from . import views

urlpatterns = [
    path('interactions/', views.log_interaction),
    path('recommendations/<int:customer_id>/', views.recommendations),
    path('trending/', views.trending),
    path('best-rated/', views.best_rated),
    path('similar/<int:book_id>/', views.similar_books),
]
