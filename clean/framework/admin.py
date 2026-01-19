from django.contrib import admin
from .models import CustomerModel, BookModel, CartModel, CartItemModel


@admin.register(CustomerModel)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)


@admin.register(BookModel)
class BookModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'stock', 'is_available', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'author')
    ordering = ('title',)
    list_editable = ('price', 'stock')


class CartItemInline(admin.TabularInline):
    model = CartItemModel
    extra = 0


@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_items', 'total_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('customer__name', 'customer__email')
    ordering = ('-created_at',)
    inlines = [CartItemInline]


@admin.register(CartItemModel)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book', 'quantity', 'subtotal', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('book__title', 'cart__customer__name')
    ordering = ('-added_at',)
