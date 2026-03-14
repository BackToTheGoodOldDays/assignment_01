from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_number', 'customer_id', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('order_number', 'customer_id')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'order', 'book_id', 'book_title', 'quantity', 'unit_price', 'subtotal')
    search_fields = ('book_title', 'book_id')
