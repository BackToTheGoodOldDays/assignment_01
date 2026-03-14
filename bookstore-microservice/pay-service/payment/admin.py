from django.contrib import admin
from .models import PaymentMethod, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('method_id', 'name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order_id', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('transaction_id', 'order_id')
