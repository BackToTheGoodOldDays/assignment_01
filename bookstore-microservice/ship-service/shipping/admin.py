from django.contrib import admin
from .models import ShippingMethod, Shipment


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('method_id', 'name', 'fee', 'estimated_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_id', 'order_id', 'tracking_number', 'shipping_method', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('tracking_number', 'order_id')
