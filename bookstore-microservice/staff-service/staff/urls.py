from django.urls import path
from . import views

urlpatterns = [
    path('staff/login/', views.login),
    path('staff/', views.staff_list),
    path('staff/<int:staff_id>/', views.staff_detail),
    path('inventory-logs/', views.inventory_logs),
]
