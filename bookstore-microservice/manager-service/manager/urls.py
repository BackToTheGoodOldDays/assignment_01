from django.urls import path
from . import views

urlpatterns = [
    path('managers/login/', views.login),
    path('managers/', views.manager_list),
    path('managers/dashboard/', views.dashboard),
    path('managers/<int:manager_id>/', views.manager_detail),
]
