from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    """Admin configuration for Customer model."""
    
    model = Customer
    list_display = ('email', 'name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
