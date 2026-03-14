from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'book_id', 'customer_id', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('book_id', 'customer_id', 'title', 'content')
