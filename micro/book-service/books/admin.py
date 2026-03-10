from django.contrib import admin
from .models import (
    BookStatus, BookTag, Book, BookImage,
    BookDescription, BookRating, BookInventory
)


@admin.register(BookStatus)
class BookStatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'status_name', 'description')
    search_fields = ('status_name',)


@admin.register(BookTag)
class BookTagAdmin(admin.ModelAdmin):
    list_display = ('tag_id', 'name', 'description')
    search_fields = ('name',)


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1


class BookDescriptionInline(admin.StackedInline):
    model = BookDescription
    extra = 0


class BookRatingInline(admin.StackedInline):
    model = BookRating
    extra = 0


class BookInventoryInline(admin.StackedInline):
    model = BookInventory
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'isbn', 'price', 'author_id', 'category_id', 'status', 'created_at')
    list_filter = ('status', 'language', 'publication_date')
    search_fields = ('title', 'isbn')
    filter_horizontal = ('tags',)
    inlines = [BookImageInline, BookDescriptionInline, BookRatingInline, BookInventoryInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'book', 'url', 'is_primary', 'display_order')
    list_filter = ('is_primary',)
    search_fields = ('book__title', 'alt_text')


@admin.register(BookDescription)
class BookDescriptionAdmin(admin.ModelAdmin):
    list_display = ('desc_id', 'book', 'short_description')
    search_fields = ('book__title', 'content')


@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    list_display = ('rating_id', 'book', 'avg_score', 'total_ratings')
    search_fields = ('book__title',)


@admin.register(BookInventory)
class BookInventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory_id', 'book', 'quantity', 'min_stock_level', 'max_stock_level', 'last_restocked')
    list_filter = ('last_restocked',)
    search_fields = ('book__title',)
