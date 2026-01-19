from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'total_items', 'total_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('customer_id',)
    ordering = ('-created_at',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book_title', 'quantity', 'subtotal', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('book_title',)
    ordering = ('-added_at',)
