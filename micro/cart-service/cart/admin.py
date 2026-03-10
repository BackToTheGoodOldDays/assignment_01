from django.contrib import admin
from .models import CartStatus, Cart, CartItem, SavedCart


@admin.register(CartStatus)
class CartStatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'name', 'description')
    search_fields = ('name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'customer_id', 'status', 'is_active', 'total_items', 'created_at', 'updated_at')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('customer_id',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'cart', 'book_id', 'quantity', 'unit_price', 'subtotal', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('book_id', 'cart__cart_id')
    readonly_fields = ('added_at', 'updated_at')


@admin.register(SavedCart)
class SavedCartAdmin(admin.ModelAdmin):
    list_display = ('saved_id', 'customer_id', 'name', 'original_cart', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_id', 'name')
    readonly_fields = ('created_at',)
