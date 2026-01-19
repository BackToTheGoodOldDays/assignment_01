from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'stock', 'is_available', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'author')
    ordering = ('title',)
    list_editable = ('price', 'stock')
