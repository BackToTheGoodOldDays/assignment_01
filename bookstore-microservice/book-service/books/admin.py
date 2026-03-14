from django.contrib import admin
from .models import Book, BookStatus, BookInventory

admin.site.register(Book)
admin.site.register(BookStatus)
admin.site.register(BookInventory)
