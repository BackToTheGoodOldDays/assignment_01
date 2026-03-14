"""Staff URL configuration."""
from django.urls import path
from store.controllers.staffController.staff_controller import (
    staff_login, staff_logout, dashboard, inventory_list,
    add_book, import_stock, bulk_import, inventory_logs,
    adjust_stock, api_inventory_status, api_quick_import,
)

app_name = 'staff'

urlpatterns = [
    path('login/', staff_login, name='login'),
    path('logout/', staff_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('inventory/', inventory_list, name='inventory_list'),
    path('inventory/add/', add_book, name='add_book'),
    path('inventory/import/', import_stock, name='import_stock'),
    path('inventory/bulk-import/', bulk_import, name='bulk_import'),
    path('inventory/logs/', inventory_logs, name='inventory_logs'),
    path('inventory/adjust/', adjust_stock, name='adjust_stock'),
    path('api/inventory-status/', api_inventory_status, name='api_inventory_status'),
    path('api/quick-import/', api_quick_import, name='api_quick_import'),
]
