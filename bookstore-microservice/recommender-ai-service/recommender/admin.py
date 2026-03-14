from django.contrib import admin
from .models import UserInteraction


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('interaction_id', 'customer_id', 'book_id', 'interaction_type', 'created_at')
    list_filter = ('interaction_type',)
    search_fields = ('customer_id', 'book_id')
