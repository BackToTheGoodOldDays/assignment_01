from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""
    
    list_display = ('id', 'customer', 'total_items', 'total_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('customer__name', 'customer__email')
    ordering = ('-created_at',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model."""
    
    list_display = ('id', 'cart', 'book', 'quantity', 'subtotal', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('book__title', 'cart__customer__name')
    ordering = ('-added_at',)
